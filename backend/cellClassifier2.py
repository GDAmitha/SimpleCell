#Tings to run passively when the page loads

#installations
# !pip install pandas
# !pip install seaborn
# !pip install numpy
# !pip install scipy
# !pip install mygene
# !pip install pickle
# !pip install sklearn
# !pip install scanpy

#importantes
import pandas as pd
import seaborn as sns
sns.set_style("whitegrid")
import pandas as pd
import numpy as np 
import scipy.stats as stats
from collections import Counter
import mygene
import pickle
import sklearn
import random
import scanpy as sc
from scipy.sparse import issparse
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.cluster import MiniBatchKMeans
import reflex as rx
import openai
openai.api_key = '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'

import hnswlib
hnswlib_imported = True

import anndata as ad

genePT_w_emebed = np.load('/Users/dimpleamithag/Documents/Git_Repos/QBIHackathon2023/SimpleCell/backend/genePT_w_emebed.npy') #DIMPLE, CHANGE TO THE CORRECT PATH
twothou = ad.read_h5ad("/Users/dimpleamithag/Documents/Git_Repos/QBIHackathon2023/SimpleCell/backend/twothou.h5ad")

class ClassifiedCell(rx.Base):
    type: str
    info: float

#Functions for data processin'
    

def get_seq_embed_gpt(X, gene_names, prompt_prefix="", trunc_index = None):
    n_genes = X.shape[1]
    if trunc_index is not None and not isinstance(trunc_index, int):
        raise Exception('trunc_index must be None or an integer!')
    elif isinstance(trunc_index, int) and trunc_index>=n_genes:
        raise Exception('trunc_index must be smaller than the number of genes in the dataset')
    get_test_array = []
    for cell in (X):
        zero_indices = [0,1]
        gene_indices = np.argsort(cell)[::-1]
        filtered_genes = gene_indices[~np.isin(gene_indices, list(zero_indices))]
        if trunc_index is not None:
            get_test_array.append(np.array(gene_names[filtered_genes])[0:trunc_index]) 
        else:
            get_test_array.append(np.array(gene_names[filtered_genes])) 
    get_test_array_seq = [prompt_prefix+' '.join(x) for x in get_test_array]
    return(get_test_array_seq)

def get_gpt_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return np.array(openai.Embedding.create(input = [text], model=model)['data'][0]['embedding'])


#Process the inputted data

userdatasample = sc.read_h5ad("/Users/dimpleamithag/Documents/Git_Repos/QBIHackathon2023/SimpleCell/backend/sample.h5ad") #DIMPLE, UPDATE

def cellClassifierFunc2(userdatapath):

    userdata = sc.read_h5ad(userdatapath) #DIMPLE, UPDATE

    
    N_TRUNC_GENE = 1000
    userdata_data = get_seq_embed_gpt(userdata.X,\
                                        np.array(userdata.var.index), 
            prompt_prefix = 'A cell with genes ranked by expression: ',trunc_index=N_TRUNC_GENE)

    userdata_gpt = []
    for x in userdata_data:
        userdata_gpt.append(get_gpt_embedding(x))
    userdata_gpt = np.array(userdata_gpt)


    y_celltype_remove_unknown = twothou.obs.celltype[np.where(twothou.obs.celltype!='Unknown')[0]]

    genePT_w_emebed_train, genePT_w_emebed_test, y_train, y_test = train_test_split(genePT_w_emebed, 
                                                        y_celltype_remove_unknown,
                                                        test_size=0.20, random_state=2023)

    k = 10  

    ref_cell_embeddings = genePT_w_emebed_train
    test_emebd = userdata.X

    if hnswlib_imported:
        # Declaring index, using most of the default parameters from https://github.com/nmslib/hnswlib
        p = hnswlib.Index(space = 'cosine', dim = ref_cell_embeddings.shape[1]) # possible options are l2, cosine or ip
        p.init_index(max_elements = ref_cell_embeddings.shape[0], ef_construction = 200, M = 16)
        
        # Element insertion (can be called several times):
        p.add_items(ref_cell_embeddings, ids = np.arange(ref_cell_embeddings.shape[0]))
        
        # Controlling the recall by setting ef:
        p.set_ef(50) # ef should always be > k

        # Query dataset, k - number of closest elements (returns 2 numpy arrays)
        labels, distances = p.knn_query(test_emebd, k = k)

    idx = labels[0]
    y_train[idx].mode()

    statement = y_train[idx].mode().to_string()
    statement = statement[5:statement.find('\n')]
    statement = str(statement)


    #return  ClassifiedCell(name=statement,info="test")
    return statement


















