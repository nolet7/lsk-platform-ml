"""Generate small synthetic CSV dataset; user uploads it to approved tenant S3."""
import argparse
from pathlib import Path
from sklearn.datasets import make_classification
import pandas as pd

def generate(path:Path,rows=500,seed=42):
    X,y=make_classification(n_samples=rows,n_features=8,n_informative=5,
                            n_redundant=1,random_state=seed)
    frame=pd.DataFrame(X,columns=[f"signal_{i}" for i in range(8)])
    frame["target"]=y
    path.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(path,index=False)
    return path

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--rows",type=int,default=500)
    args=p.parse_args()
    generate(args.output,args.rows)
