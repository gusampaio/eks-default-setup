import sys, argparse, os
import urllib.request
import subprocess as sp

arn = sp.getoutput("kubectl config current-context")
clusterName = arn.split("/")[-1]
defaultPath = os.getcwd() + "/k8s"

def main():
    dispatcher = { 'all': createAll , 
                   'cluster_autoscaler': createCA ,
                   'horizontal_pod_autoscaler': createHPA,
                   'dashboard': createMetricServer
                }
    
    # Create default folder to store all config
    createLocalDir("k8s")

    # receive the arguments passed at the initailization of the command
    functions = buildArguments()
    
    for f in functions:
        dispatcher[f]()


def createAll():
    print("Installing everything")

def setDeafultConfig(folderName,url,cmd):
    
    createLocalDir(folderName)
    downlodaTemplate(url, folderName)
    # applying commnad deffined
    os.system(cmd)
    # Applying k8s commands
    kubectlApply(folderName)
    # Going Back to Default dir
    os.chdir(defaultPath)


# Metric Server
def createMetricServer():
    print("Installing K8s Metrics")
    name = "metric-server"
    gistURL = 'https://github.com/kubernetes-sigs/metrics-server/' \
              'releases/download/v0.3.6/components.yaml'
    cmd = """cat << EOF  > eks-admin-service-account.yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
    name: eks-admin
    namespace: kube-system
    ---
    apiVersion: rbac.authorization.k8s.io/v1beta1
    kind: ClusterRoleBinding
    metadata:
    name: eks-admin
    roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: cluster-admin
    subjects:
    - kind: ServiceAccount
    name: eks-admin
    namespace: kube-system
    EOF"""

    setDeafultConfig(name,gistURL,cmd)
    # Create metric Server and Dashboard 
    createDashboard()


 #  K8s-dashboard 
def createDashboard():
    print("Installing Dashboard")
    name = 'dashboard'
    gistURL = 'https://raw.githubusercontent.com/kubernetes/dashboard/' \
            'v2.0.0-beta8/aio/deploy/recommended.yaml'
    cmd = ''
    # Create service account: https://docs.aws.amazon.com/eks/latest/userguide/dashboard-tutorial.html
    setDeafultConfig(name,gistURL,cmd)
    os.system("kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep eks-admin | awk '{print $1}')")


# Create Cluster AutoScaler Folders and apply commands 
def createCA():    
    print("Installing CA...")
    
    name = "CA"
    gistURL = 'https://raw.githubusercontent.com/kubernetes/' \
              'autoscaler/master/cluster-autoscaler/cloudprovider/' \
              'aws/examples/cluster-autoscaler-autodiscover.yaml'
    dirFileName = "cluster-autoscaler-autodiscover.yaml"
    
    # Updating template with Correct Cluster Name
    cmd = "sed -i'.original' -e 's/<YOUR CLUSTER NAME>/" + clusterName + "/g' " + dirFileName
    setDeafultConfig(name, gistURL, cmd)
    print("Retrieving authentication token for the eks-admin service account")


# Horizontal Pod AutoScaler
def createHPA():
    # Creating local
    print(defaultPath)


def downlodaTemplate(url, fileName):
    fileName = fileName + ".yaml"
    urllib.request.urlretrieve(url, fileName)


def kubectlApply(path):
    os.system("kubectl apply -f " + path)


def createLocalDir(name):
    try:
        os.mkdir(name)
        print("Directory " , name , " has been created")
        print("Changing to dir")
    except FileExistsError:
        print("Directory " , name ,  " already exists, skipping...")
            
    os.chdir(name)


def buildArguments():
    # Building args to pass over the desired ones
    parser = argparse.ArgumentParser(description='Execute Kubernetes commands to deploy Commons addons to your Cluster')
    # group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("-A", "--all", help="Install all Add ons to your Cluster", action="store_true")
    parser.add_argument("-ca", "--cluster-autoscaler", help="Install Cluster Auto Scaler", action="store_true")
    parser.add_argument("-hpa", "--horizontal-pod-autoscaler", help="Install Horizontal Pod Auto Scaler", action="store_true")
    parser.add_argument("-D", "--dashboard", help="Install Kubernetes Dashboard and metrics", action="store_true")
    args = parser.parse_args()
    argsTrue = []

    # It will iterate for all args chosen and append to a list
    for arg in vars(args):
       if  getattr(args, arg):
           argsTrue.append(arg)
    
    return argsTrue


if __name__ == "__main__":
    main()


