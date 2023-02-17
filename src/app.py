from web3 import Web3, HTTPProvider
from flask import Flask, render_template, redirect, request,session
import json
import re
import math
from datetime import datetime
import os
import hashlib

def hash_file(filename):
    h=hashlib.sha1()
    with open(filename,'rb') as file:
        chunk=0
        while chunk!=b'':
            chunk=file.read(1024)
            h.update(chunk)
    return h.hexdigest()

api=Flask(__name__) # launching a Flask apilication (API Server)
api.secret_key='sacet14a'
api.config['uploads']='static/uploads'

def connect_blockchain_register(acc): # which connects with blockchain server
    blockchain='http://127.0.0.1:7545'
    web3=Web3(HTTPProvider(blockchain)) # it sends a client request to blockchain server
    if acc==0: # load the primary account
        acc=web3.eth.accounts[0]
    web3.eth.defaultAccount=acc
    artifact_path="../build/contracts/register.json" # load the artifact deployed on blockchain
    with open(artifact_path) as f:
        contract_json=json.load(f) # convert string to json object
        contract_abi=contract_json['abi'] # load the abi (API) of Blockchain
        contract_address=contract_json['networks']['5777']['address'] # select contract address
    contract=web3.eth.contract(address=contract_address,abi=contract_abi) # send contract request
    return(contract,web3)

def connect_blockchain_plagiarism(acc): # to connect with plagiarism contract
    blockchain='http://127.0.0.1:7545' # blockchain server
    web3=Web3(HTTPProvider(blockchain)) # connecting with ganache
    if acc==0: # loading the primary account
        acc=web3.eth.accounts[0]
    web3.eth.defaultAccount=acc # making acc as default
    artifact_path="../build/contracts/plagiarism.json" # load the artificat
    with open(artifact_path) as f:
        contract_json=json.load(f) # convert to json object
        contract_abi=contract_json['abi'] # load the abi (API) of Blockchain
        contract_address=contract_json['networks']['5777']['address'] # select contract address
    contract=web3.eth.contract(address=contract_address,abi=contract_abi) # send contract request
    return(contract,web3)

def cosineSimilarity(k): # find out the similarity of database with input text
        universalSetOfUniqueWords=[] # Universal Words Lit
        matchPercentage=0 # percentage of matched
        
        inputQuery=k # laoding the input query
        lowercaseQuery=inputQuery.lower() # converting it into lowercase

        queryWordList=re.sub("[^\w]"," ",lowercaseQuery).split() # splitting the sentences into words

        for word in queryWordList: # processign each word in words list of query
            if word not in universalSetOfUniqueWords: # store only unique words
                universalSetOfUniqueWords.append(word)
        
        f=open('dataset.txt','r') # read the dataset
        db=f.read().lower() # convert into lowercase
        f.close()

        dbWordList=re.sub("[^\w]"," ",db).split() # splitting sentences into words
        
        for word in dbWordList: # processing each word in database words list
            if word not in universalSetOfUniqueWords: # store only unique words
                universalSetOfUniqueWords.append(word)

        queryTF=[]
        dbTF=[]

        for word in universalSetOfUniqueWords: # count how many words and successive words gets matched
            queryTFcount=0
            dbTFcount=0
            
            for word2 in queryWordList: # counting in query list with universal words list
                if word==word2:
                    queryTFcount+=1
            queryTF.append(queryTFcount) # store the count value of word 
            
            for word2 in dbWordList: # counting in database list with universal words list
                if word==word2:
                    dbTFcount+=1
            dbTF.append(dbTFcount) # store the count value of word repeating in db

        dotProduct=0 # compute the dot product between query and db
        for i in range(len(queryTF)):
            dotProduct+=queryTF[i]*dbTF[i]

        queryVectorMagnitude=0 # calculate the magnitude of query
        for i in range(len(queryTF)):
            queryVectorMagnitude+=queryTF[i]**2
        queryVectorMagnitude=math.sqrt(queryVectorMagnitude) 
            
        databaseVectorMagnitude=0 # calculate the magniture of db
        for i in range(len(dbTF)):
            databaseVectorMagnitude+=dbTF[i]**2
        databaseVectorMagnitude=math.sqrt(databaseVectorMagnitude)
        
        matchPercentage=(float)(dotProduct/(queryVectorMagnitude*databaseVectorMagnitude))*100 #apply cosine similarity
        print(matchPercentage)
        matchPercentage="%0.02f"%matchPercentage # only upto two decimal places
        print(matchPercentage)
        return matchPercentage
    

@api.route('/') # API to access the Home Page of apilication
def homePage():
    return render_template('index.html')

@api.route('/registerForm',methods=['post']) # API which collects data from user and stores in blockchain
def registerForm():
    walletaddr=request.form['walletaddr'] # collecting details from HTML Form
    name=request.form['name']
    email=request.form['email']
    password=request.form['password']
    print(walletaddr,name,email,password)

    contract,web3=connect_blockchain_register(0) # connecting to register contract on blockchain
    try: # sending a transaction request to store this details onto the blockchain
        tx_hash=contract.functions.registeruser(walletaddr,int(password),name,email).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return (render_template('index.html',res='Registered Successfully'))
    except: # An exception is raised when account exist in blockchain
        return (render_template('index.html',err='Already Registered'))

@api.route('/login') # rendering the login page to user
def loginPage(): 
    return render_template('login.html')

@api.route('/loginForm',methods=['post']) # API which collects data from Login Form
def loginForm():
    walletaddr=request.form['walletaddr'] # details from login form
    password=request.form['password']
    print(walletaddr,password)

    try:
        contract,web3=connect_blockchain_register(0) # connect to blockchain
        state=contract.functions.loginuser(walletaddr,int(password)).call() # call the contract function
        if(state==True): # both username and password are matched
            session['username']=walletaddr
            return(redirect('/dashboard')) # success
        else:
            return render_template('login.html',err='Invalid details') # error
    except:
        return render_template('login.html',err='You are a new user, you have to register first') # error

@api.route('/dashboard') # to render dashboard page to user after successful login
def dashboardPage():
    return render_template('dashboard.html')

@api.route('/logout') # logout page
def logoutPage():
    session['username']=None
    return redirect('/')

@api.route('/checkPlagiarism',methods=['post']) #api to check plagiarism 
def checkPlagiarism():
    textInput=request.form['textinput'] # collect data
    print(textInput)
    p=cosineSimilarity(textInput) # pass data to cosine similarity
    print(p)

    tmp=str(datetime.now()) # capture date and time
    tmp=tmp.split(' ') # seperate date and time
    tmp=tmp[0]+tmp[1] # append them without space
    tmp=tmp+'.txt' # add the txt extension

    if session['username'] not in os.listdir(api.config['uploads']): # create directory
        os.mkdir(os.path.join(api.config['uploads'],session['username']))

    with open(os.path.join(api.config['uploads'],session['username']) + '/' + tmp + '.txt','w') as f1:  # store the file in uploads folder for backup 
        f1.write(textInput)
    
    hash=hash_file(os.path.join(api.config['uploads'],session['username']) + '/' + tmp + '.txt') # compute hash for the file
    try: # add document to the blockchain
        contract,web3=connect_blockchain_plagiarism(0)
        tx_hash=contract.functions.adddocument(session['username'],hash).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        with open('dataset.txt','a') as f0: # append the textinput with database
            f0.write(textInput)
        return (render_template('dashboard.html',res=f'{p} % Matched'))
    except:
        print('Already Enrolled into blockchain')
        return (render_template('dashboard.html',res=f'{p} % Matched'))

if (__name__=="__main__"): # Run the API Server
    api.run(debug=True,port=5001)