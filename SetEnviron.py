import os

def SetEnviron():
    with open('.env', 'r') as f:
        environs = f.readlines()
    for env in environs:
        key = env.split("=")[0].strip()
        value = env.split("=")[1].strip()
        os.environ[key] = value