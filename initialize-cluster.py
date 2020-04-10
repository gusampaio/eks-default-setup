import sys, argparse

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

def createCA():
    print("Installing CA")

def createHPA():
    print("Installing HPA")   

def buildArguments():
    # Building args to pass over the desired ones
    parser = argparse.ArgumentParser(description='Execute Kubernetes commands to deploy Commons addons to your Cluster')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", "-A", help="Install all Add ons to your Cluster", action="store_true")
    group.add_argument("--cluster-autoscaler", "-ca", help="Install Cluster to your Cluster", action="store_true")
    group.add_argument("--horizontal-pod-autoscaler", "-hpa", help="Install Cluster to your Cluster", action="store_true")
    args = parser.parse_args()
    argsTrue = []

    # It will iterate for all args chosen and append to a list
    for arg in vars(args):
       if  getattr(args, arg):
           argsTrue.append(arg)
    
    return argsTrue


if __name__ == "__main__":
    main()


