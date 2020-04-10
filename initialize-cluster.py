import sys, argparse, os
import urllib.request
import subprocess as sp

arn=sp.getoutput("kubectl config current-context")
print(arn)
clusterName=arn.split("/")[-1]

def main():
    dispatcher = { 'all': createAll , 
                   'cluster_autoscaler': createCA ,
                   'horizontal_pod_autoscaler': createHPA
                }
    
    # receive the arguments passed at the initailization of the command
    functions = buildArguments()
    
    for f in functions:
        dispatcher[f]()


def createAll():
    print("Installing everything")

# Create Cluster AutoScaler Folders and apply commands 
def createCA():    
    print("Installing CA...")
    
    name="CA"
    gistURL="https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml"
    dirFileName=name + "/cluster-autoscaler-autodiscover.yaml"
    
    # Creating local directory
    createLocalDir(name)
    # Downloading template
    downlodaTemplate(gistURL, dirFileName)
    # Updating template with Correct Cluster Name
    cmd="sed 's/<YOUR CLUSTER NAME>/" + clusterName + "/' " + dirFileName
    print(cmd)
    os.system(cmd)



    # Applying commands
    kubectlApply(dirFileName,name)


# Horizontal Pod AutoScaler
def createHPA():
    # Creating local
    print("oi")



def downlodaTemplate(url, fileName):
    urllib.request.urlretrieve(url, fileName)

def kubectlApply(path,name):
    os.system("kubectl apply -f " + path)
    print("Deployed ", name)

def createLocalDir(name):
    try:
        os.mkdir(name)
        print("Directory " , name , " has been created")
    except FileExistsError:
        print("Directory " , name ,  " already exists")

def buildArguments():
    # Building args to pass over the desired ones
    parser = argparse.ArgumentParser(description='Execute Kubernetes commands to deploy Commons addons to your Cluster')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-A", "--all", help="Install all Add ons to your Cluster", action="store_true")
    group.add_argument("-ca", "--cluster-autoscaler", help="Install Cluster to your Cluster", action="store_true")
    group.add_argument("-hpa", "--horizontal-pod-autoscaler", help="Install Cluster to your Cluster", action="store_true")
    args = parser.parse_args()
    argsTrue = []

    # It will iterate for all args chosen and append to a list
    for arg in vars(args):
       if  getattr(args, arg):
           argsTrue.append(arg)
    
    return argsTrue


if __name__ == "__main__":
    main()


