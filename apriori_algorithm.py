# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 16:40:05 2015

@author: Rohan Kulkarni(rk2845)
         Aishwarya Rajesh(ar3567)
"""

import csv
from itertools import combinations
import itertools
import operator
import sys

class APRIORI_ALGORITHM:
    _minimumSupport=0
    _minimumConfidence=0

    def __init__(self,minSup,minConf):
        self._minimumSupport=float(minSup)
        self._minimumConfidence=float(minConf)
   
    def getMinimumSupport(self):
        return self._minimumSupport
    
    def getMinimumConfidence(self):
        return self._minimumConfidence
    
    def generateDatabase(self,ylist):
        '''
        Generate Initial market baskets of items from the dataset
        '''
        parentList=[]
        for i in xrange(1,len(ylist)):
            childList=[]
            for j in xrange(len(ylist[i])):
                if ylist[i][j]=='1':
                    childList.append(ylist[0][j])
                elif ylist[i][j]=='0':
                    pass
                else:
                    childList.append(ylist[i][j])
            parentList.append(sorted(childList))  
        return parentList
        
    def generateInitialLargeItemsets(self,D):
        '''
        Generates large itemsets for single items
        '''
        itemCount={}
        for i in xrange(len(D)):
            for j in xrange(len(D[i])):
                if itemCount.has_key(D[i][j]):
                    itemCount[D[i][j]]+=1
                else:
                    itemCount[D[i][j]]=0
        for k,v in itemCount.items():
            itemCount[k]=float(v) / float(len(D))
    
        for eachKey in itemCount.keys():
            if itemCount[eachKey] < self.getMinimumSupport():
                itemCount.pop(eachKey)
        return itemCount
    
    def calculateSupport(self,CI,D):
        '''
        Generates the large itemsets for higher order 
        '''
        countDict={}
        i=0    
        while i < len(CI)-1:
            j=i+1
            #Generate all permutations of a market basket
            perm=itertools.permutations(CI[i])
            g=[]
            for each in perm:
                g.append(list(each))
            lengthCI=len(CI)
            while j < lengthCI:         
                if CI[j] in g:
                    del CI[j]
                    lengthCI-=1
                j+=1     
            i+=1
        # Calculate the counts of all the items 
        for each_itemset in CI:
            for i in xrange(len(D)):
                 if set(D[i]).issuperset(each_itemset):   
                    if tuple(sorted(each_itemset)) in countDict.keys():
                         countDict[tuple(sorted(each_itemset))]+=1
                    else:
                         countDict[tuple(sorted(each_itemset))]=1
           
        for k,v in countDict.items():
            countDict[k]=float(v) / float(len(D))
        
        for eachKey in countDict.keys():
            if countDict[eachKey] < self.getMinimumSupport():
                countDict.pop(eachKey)
        return countDict            
    
    def pruneItemsets(self,CI,lastFrequent,order):
        '''
        Eliminate the infrequent itemsets from the candidate item list if any
        of their subsets arent frequent
        '''
        for each_itemset in CI:
            subsets=list(combinations(each_itemset,order))        
            for each in subsets:
                if order==1:
                    each=list(each)
                    for e in each:
                        if e not in lastFrequent:
                            CI.pop(CI.index(each_itemset))
                            break
                else:
                    if each not in lastFrequent:
                        CI.pop(CI.index(each_itemset))
                        break
        return CI
    
    def genCandidateItemsets(self,l,counter):
        '''
        Generate candidate itemsets for higher orders
        '''
        finalList=[]
        for i in xrange(len(l)):
            l[i]=set(l[i])
        for i in xrange(len(l)-1):
            j=i+1
            while j<len(l):
                q=l[i].union(l[j])
                if len(q) == counter:
                    if list(q) not in finalList:
                        finalList.append(list(q))
                j+=1
        return finalList
   
    def mineStrongRules(self,mainList):
        '''
        Generate association rules from the frequent itemsets based on minimum
        support and confidence values.
        '''
        l=[]
        for every in mainList:
            if type(every['subset'])==str:
                every['subset']=every['subset'].split('\r')
            l.append(every)  
        
        rules={}
        supRules={}
        for k in l:
            if len(k['subset'])>=2:
                #Generating rule with one item on the RHS
                for each in k['subset']:
                    t=[]
                    t.append(each)
    
                    temp=[item for item in k['subset'] if item!=each] 
                    lhsSup=[p for p in mainList if p['subset']==temp]
                    #Calculating confidence of rule
                    confidence=float(k['sup'])/float(lhsSup[0]['sup'])
                    
                    #Recording high-confidence rules
                    if confidence>=self.getMinimumConfidence():
                        rule='[%s]=>[%s]'%((','.join(temp)),t[0])
                        rules[rule]=confidence
                        supRules[rule]=k['sup']
        
        return (rules,supRules)

    def createOutputFile(self,largeItemset,assocRules,supRules):
        '''
        Creating output.txt file as required
        '''
        f=open('output.txt','w')
        header='==FREQUENT ITEMSETS (min_supp='+str(self.getMinimumSupport()*100)+'%)\n\n'
        f.write(header)
    
        #Printing frequent itemsets to file in decreasing order of support
        sortedItemset = sorted(largeItemset, key=operator.itemgetter('sup'), reverse=True)
        
        for every in sortedItemset:
            line=str(every['subset'])+', '+str(every['sup']*100)+'%\n'
            f.write(line)
        f.write('\n')
        
        #Printing high-confidence association rules to file in decreasing order of confidence
        header='==HIGH-CONFIDENCE ASSOCIATION RULES (min_conf='+str(self.getMinimumConfidence()*100)+'%)\n\n'
        f.write(header)
    
        sortedRules = sorted(assocRules.items(), key=operator.itemgetter(1), reverse=True)
        
        for every in sortedRules:
            line=str(every[0])+' (Conf: '+str((every[1])*100)+'%, Supp: '+str((supRules[every[0]])*100)+'%)\n'
            f.write(line)
            

def main():
    #Accepting command-line input of filename, minimum support and minimum confidence
    filename=sys.argv[1]
    minSup=sys.argv[2]
    minConf=sys.argv[3]
    
    allSupportCount={}
    #Read from the integrated dataset file
    with open(filename,'r') as f:
        reader=csv.reader(f)
        ylist=list(reader)
        
    #instantiate the APRIORI_ALGORITHM class
    obj=APRIORI_ALGORITHM(minSup,minConf)
    #Build the initial transaction list
    initialTransactions=obj.generateDatabase(ylist)
    #Build initial large itemset list
    initialLI=obj.generateInitialLargeItemsets(initialTransactions)
    allSupportCount.update(initialLI)

    counter=2
    while True:
        if counter==2:
            #get candidate itemsets for order 2
            CI=list(combinations(initialLI.keys(),counter))
            CI_list = [list(item) for item in CI]
        else:
            #get candidate itemsets for higher orders
            CI_list=obj.genCandidateItemsets(initialLI.keys(),counter)
        
        #Get the large itemsets
        tempLI=obj.calculateSupport(CI_list,initialTransactions)
        allSupportCount.update(tempLI)
        
        #Pruning Step
        prunedCI=obj.pruneItemsets(CI_list,initialLI.keys(),counter-1)
        prunedCI.sort()
        prunedCI=list(prunedCI for prunedCI,_ in itertools.groupby(prunedCI))
        newLI=obj.calculateSupport(prunedCI,initialTransactions)
        
        if len(newLI) == 0:
            break
        initialLI=dict(newLI)
        counter+=1

    mainList=[]
    for every in allSupportCount.keys():
        temp={}
        if type(every)==str:
            temp['subset']=every
            temp['sup']=allSupportCount[every]
            mainList.append(temp)
        else:
            temp['subset']=list(every)
            temp['sup']=allSupportCount[every]
            mainList.append(temp)
   
    (assocRules,supRules)=obj.mineStrongRules(mainList)
    obj.createOutputFile(mainList,assocRules,supRules)
    print "ASSOCIATION RULES GENERATED IN FILE 'output.txt'"    
    
if __name__=='__main__':
    main()
    