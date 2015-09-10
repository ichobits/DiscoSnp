#!/bin/python
# -*- coding: utf-8 -*-
###############################################
#Dresscode : class : uppercase
#            function : begins with a capital
#            variable : words separated by capital
#            object : words separated by underscore
from functionObjectVCF_creator import *
import re
import os
import sys
import subprocess
import re
import time


#Class and methods_________________________________________________________________________________________________________
#INDEX_____________________________________________________________________________________________________________
#________________class VARIANT(): corresponds to a discosnp bubble with information common to both paths________________ 
#   ______
#__/      \__
#  \______/
# => Methods
#      FillInformationFromHeader(self,VCFObject):"""Parsing of the DiscoSnp++ header"""
#      ReverseComplement(self,nucleotide):"""Take a sequence or a nucleotide and reverse it"""
#      CheckContigUnitig(self,unitig,contig):"""Checks if there is an extension in the form of contig or unitig to take into account in the mapping position"""
#      GetPolymorphismFromHeader(self):'''Gets from the dicoAllele all the positions, and the nucleotides'''
#      MismatchChecker(self):"""In case of divergent main position (case snp whose two paths are mapped ) to define the reference = > check the number of mismatch
#                               ( If the number of mismatch is the same in both cases it is the lower lexicographical SNP which is selected for reference .
#                                The Boolean allows to know the reference SNP ) """      
#      GetGenotypes(self,nbGeno,VCFObject):"""Gets the genotype, the coverage and the likelihood by sample and print it in the correspondand fields. The genotype is determined by DiscoSnp++ (which considered the upper path as reference). If the “REF” corresponds the upper path, the genotype in the VCF is identical to the genotype in DiscoSnp++, else  it's the opposite ( 1/1 becomes 0/0 and so on)."""     
#      FillVCF(self,VCFfile,nbGeno,table,VCFObject): """Take all necessary input variables to fill the vcf;  Fills the fields of the table which will be printed in the vcf ; return the table"""  
#      WhichPathIsTheRef(self,VCFObject): """Finds which path is identical to the reference genome and defines it as the ref : specific method for each type of variant""" 
#      GetMappingPositionCouple(self): """Defines the mapping position for the couple of variant"""
#      CheckStrandAndReverseNucleotide(self,nucleo):"""Reverse the alt nucleotide if it is needed"""     
#      CheckCoupleVariantID(self):"""Test if the couple of paths has the same ID"""

#________________class PATH(): """corresponds to one path"""________________
#      GetSeq(self,seq):"""Getter for sequence"""
#      GetDicoMappingPosition(self):"""Retrieves for each path alignment information in a list ; retrieves a dictionary with all the positions of a path and the number of associated mismatch"""
#      CheckBitwiseFlag(self):"""Checks if the BitwiseFlag contains the tested value such as : read reverse strand, read unmmaped and so on."""
#      CigarcodeChecker(self):"""Checks in the cigarcode of the samfile if there is a shift in the alignment between the path and the reference"""
#      ReferenceChecker(self,shift,posCentraleRef,VCFObject):"""Function which allows to get the MD tag parsing; checks if path nucleotide is identical to the reference nucleotide"""
#      GetCoverage(self):"""Get the coverage by path in the discosnp++ header"""
#      GetTag(self):"""Gets the number of mismatch in the samline"""
#      CheckPosVariantFromRef(self,VCFObject): """Checks if the variant is identical to the reference or not ; defines the nucleotide on the reference"""

#________________class SNP(VARIANT):________________
#       WhichPathIsTheRef(self,VCFObject):""""""

#________________class INDEL(VARIANT):________________
#      GetPolymorphismFromHeader(self):""""""
#      WhichPathIsTheRef(self,VCFObject):""""""
#      GetMappingPositionCouple(self):""""""

#________________class SNPSCLOSE(VARIANT):________________
#      GetDicoClose(self,dicoCloseUp,dicoCloseLow):
#      WhichPathIsTheRef(self,VCFObject):
#      FillVCF(self,VCFfile,nbGeno,table,VCFObject):

#________________class VCFFIELD():________________
#      PrintOneLine(self,table,VCF):


class VARIANT():
        """Object corresponding to a discosnp++ bubble"""
        def __init__(self,line1,line2):
                self.upper_path=PATH(line1)#line in the file corresponding to the upper path
                self.lower_path=PATH(line2)#line in the file corresponding to the lower path
                self.variantID="" #ID of discoSnp++
                self.discoName=""#name of the variant : SNP_higher_path_99
                self.unitigLeft=""#length of the unitig left
                self.unitigRight=""#length of the unitig right
                self.contigLeft=""#length of the contig left
                self.contigRight=""#length of the contig right
                self.rank=""#rank calculated by discosnp++
                self.nb_pol=""# number of polymorphisme in the disco path 
                self.dicoGeno={}#dictionnary with the information of the genotype dicoGeno[listgeno[0]]=[listgeno[1],listlikelihood]
                self.dicoAllele={}#dictionnary of all the information from the header of discosnp++ : depending on the variant
                self.mappingPositionCouple=0#mapping position of the bubble after correction

#---------------------------------------------------------------------------------------------------------------------------
##Example :SNP_higher_path_99|P_1:30_A/C|high|nb_pol_1|left_unitig_length_129|right_unitig_length_901|C1_0|C2_30|G1_1/1:744,116,6|G2_0/0:6,95,604|rank_1.00000
#---------------------------------------------------------------------------------------------------------------------------                                           
        def FillInformationFromHeader(self,VCFObject):
                """Parsing of the DiscoSnp++ header"""
                headerVariantUp=self.upper_path.listSam[0]#header of the upper path
                headerVariantLow= self.lower_path.listSam[0]#header of the lower path
                discoList=headerVariantUp.split('|')#splitting the header of discosnp++ into a list
                self.discoName=discoList[0]#fills the attribut discoName of the variant object
                self.variantID=self.discoName.split("_")[3]#Gets the variantID ex:56468
                VCFObject.variantType=self.discoName.split("_")[0]#fills the VCF object with the variant type
                listgeno=[]#splitted informations by genotype contained in the header of discoSnp++
                for name in discoList:# Loops on the header of discoSnp++
                        if 'P_1' in name:#P_1:30_A/G => {'P_1': ['30', 'A', 'G']} or P_1:30_A/G,P_2:31_G/A
                                pos=name.split(',')
                                for item in pos:
                                        if VCFObject.variantType=="SNP":#Specific dictionary dicoAllele in case of simple snp
                                                if ":" in item:
                                                        listP_=item.split(":")
                                                        self.dicoAllele[listP_[0]]=[(listP_[1].split("_")[0]),(listP_[1].split("_")[1].split("/")[0]),(listP_[1].split("_")[1].split("/")[1])]#{'P_1': ['30', 'A', 'G']}
                                        elif VCFObject.variantType=="INDEL":#INDEL case : P_1:30_3_2 => {'P_1': ['30', '3', '2']} specific to the INDEL
                                                listP_=item.split(":")
                                                self.dicoAllele[listP_[0]]=[(listP_[1].split("_")[0]),(listP_[1].split("_")[1]),(listP_[1].split("_")[2])]#  {'P_1': ['30', '3', '2']}                         
                        elif "unitig" in name:
                                if "left" in name:
                                        self.unitigLeft=name.split("_")[3]
                                if "right" in name:
                                        self.unitigRight=name.split("_")[3]                                        
                        elif "contig" in name:
                                if "left" in name:
                                        self.contigLeft=name.split("_")[3]
                                if "right" in name:
                                        self.contigRight=name.split("_")[3]
                        elif "rank" in name:
                                self.rank=name.split('_')[1]
                        elif "nb_pol" in name:
                                self.nb_pol=int(name.split('_')[2])                                                               
                        elif "G" in name: #Gets the genotype and likelihood by samples
                               matchG=re.match(r'^G',name)# finds the genotype in the item of the dicoSnp++ header
                               if matchG:
                                       listgeno=name.replace("_",":").split(":")
                                       if len(listgeno)>2:
                                                self.dicoGeno[listgeno[0]]=[listgeno[1],(listgeno[2].split(','))]
                                       else:                                     
                                                self.dicoGeno[listgeno[0]]=[listgeno[1]]
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                           
        def ReverseComplement(self,nucleotide):
                """Take a sequence or a nucleotide and reverse it"""
                if len(nucleotide)==1:#nucleotide 
                        if nucleotide=="A": return "T"
                        if nucleotide=="T": return "A"
                        if nucleotide=="C": return "G"
                        return "C"
                elif len(nucleotide)>1:#Sequence
                        i=0
                        listSeq=list(nucleotide)
                        seq=''
                        while i<len(listSeq):
                                if seq!='':#adds the nucleotide to the already reversed sequence
                                        seq=str(self.ReverseComplement(listSeq[i]))+seq
                                else :#first nucleotide of the sequence
                                        seq=str(self.ReverseComplement(listSeq[i]))
                                i+=1
                        return(seq)
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
        def CheckContigUnitig(self,unitig,contig):
                """Checks if there is an extension in form of contig or unitig to take into account in the position of the variant on the path"""
                if contig:#we keep the length of the contig to add it in the event of unmapped path
                        return(int(contig))#return the contig length
                elif unitig:# if there is not a contig we keep the length of the unitig
                        return(int(unitig))#return the unitig length
                else:
                        return 0
                                                                                                                                                                                                                                      
        #def FillInformationFromSequence():
        ##TODO
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                                   
        def GetPolymorphismFromHeader(self):
                '''Gets from the dicoAllele all the positions, and the nucleotides for each variant '''
                for key,(posD,ntUp,ntLow) in self.dicoAllele.items(): #Goes through the dictionary of parsed header
                        self.upper_path.listPosForward.append(int(posD)+1)
                        self.lower_path.listPosForward.append(int(posD)+1)
                        self.upper_path.listPosReverse.append(len(self.upper_path.seq)-int(posD))
                        self.lower_path.listPosReverse.append(len(self.upper_path.seq)-int(posD))
                        self.upper_path.listNucleotideForward.append(ntUp)
                        self.lower_path.listNucleotideForward.append(ntLow)
                        self.upper_path.listNucleotideReverse.append(self.ReverseComplement(ntUp))
                        self.lower_path.listNucleotideReverse.append(self.ReverseComplement(ntLow))
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                                    
        def MismatchChecker(self):
                """In case of divergent main position (case snp whose two paths are mapped ) to define the reference = > check the number of mismatch
        ( If the number of mismatch is the same in both cases it is the lower lexicographical SNP which is selected for reference .
        The Boolean allows to know the reference SNP ) """
                nmUp=None
                nmLow=None
                #Two paths mapped
                if int(self.upper_path.mappingPosition)>0 and int(self.lower_path.mappingPosition)>0:#Checks if both paths are mapped 
                        nmUp=int(self.upper_path.dicoMappingPos[self.upper_path.mappingPosition]) #Distance with the reference for the snpUp
                        nmLow=int(self.lower_path.dicoMappingPos[self.lower_path.mappingPosition]) #Distance with the reference for the snpLow
                        if nmUp<nmLow: #Checks if the upper path has a distance with the reference smaller than the lower path
                                self.lower_path.boolRef=False
                                self.upper_path.boolRef=True 
                                self.lower_path.nucleoRef=self.upper_path.nucleoRef
                                self.mappingPosition=self.upper_path.mappingPosition
                        elif nmUp>nmLow :#Checks if the lower path has a distance with the reference smaller than the upper path
                                self.lower_path.boolRef=True
                                self.upper_path.boolRef=False
                                self.upper_path.nucleoRef=self.lower_path.nucleoRef
                        elif nmUp==nmLow: #Checks if both path have the same number of difference
                                if self.discoName.split("_")[0]!="INDEL": #In case of simple snp
                                        if  self.upper_path.nucleo<self.lower_path.nucleo: #Checks the lexicographical order
                                                self.lower_path.boolRef=False
                                                self.upper_path.boolRef=True
                                                self.lower_path.nucleoRef=self.upper_path.nucleoRef
                                                self.mappingPosition=self.upper_path.mappingPosition
                                        elif  self.upper_path.nucleo> self.lower_path.nucleo: #Checks the lexicographical order
                                                self.lower_path.boolRef=True
                                                self.upper_path.boolRef=False
                                                self.upper_path.nucleoRef=self.lower_path.nucleoRef
                                        else : #If none of the alleles is lexicographically less : checks the mapping position and keeps the lefmost position
                                                if int(self.upper_path.mappingPosition)<int(self.lower_path.mappingPosition):
                                                        self.lower_path.boolRef=False
                                                        self.upper_path.boolRef=True
                                                        self.lower_path.nucleoRef=self.upper_path.nucleoRef
                                                else:
                                                        self.lower_path.boolRef=True
                                                        self.upper_path.boolRef=False
                                                        self.upper_path.nucleoRef=self.lower_path.nucleoRef
                                else: #In case of indel
                                        if int(self.upper_path.mappingPosition)<int(self.lower_path.mappingPosition): #Checks the mapping position and keeps the lefmost position
                                                self.lower_path.boolRef=False
                                                self.upper_path.boolRef=True
                                        else:
                                                self.lower_path.boolRef=True
                                                self.upper_path.boolRef=False
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
        def GetGenotypes(self,nbGeno,VCFObject):
                """Gets the genotype, the coverage and the likelihood by sample and prints it in the corresponding fields. The genotype is determined by DiscoSnp++ (which considered the upper path as reference). If the “REF” corresponds the upper path, the genotype in the VCF is identical to the genotype in DiscoSnp++, else  it's the opposite ( 1/1 becomes 0/0 and so on)."""
                j=0
                genotypes=""
                key=None
                current_genotype=None
                likelihood=None
                coverage=None
                listcovUp=self.upper_path.listCoverage
                listcovLow=self.lower_path.listCoverage
                if int(nbGeno)==0:
                        return
                else:
                        for i in range(0,nbGeno): #for each genotype
                                coverage=str(listcovUp[i])+","+str(listcovLow[i])#defines allele depth 
                                key="G"+str(i+1) # Creates the dictionary key
                                current_genotype = self.dicoGeno[key]#Gets the genotypes associated to the key
                                likelihood=current_genotype[1]#Gets the likelihood associated to the key
                                if self.lower_path.boolRef==True: #Checks if the mapped path is the lower (in this case exchange 0/0 to 1/1 and 1/1 to 0/0 ; exchanges the likelihood to have the good one for each genotypes)
                                        coverage=str(listcovLow[i])+","+str(listcovUp[i])#Inverts the coverage
                                        #Inverts the first and the last likelihood
                                        likelihoodStart=likelihood[2]
                                        likelihoodEnd=likelihood[0]
                                        likelihood[0]=likelihoodStart
                                        likelihood[2]=likelihoodEnd
                                        #Inverts the genotype
                                        if "1/1" in current_genotype[0]:
                                                current_genotype[0]=current_genotype[0].replace("1/1","0/0")
                                        elif "0/0" in current_genotype[0]:
                                                current_genotype[0]=current_genotype[0].replace("0/0","1/1")
                                if VCFObject.phased==True: #In case of phasing we change the "/" symbol
                                    current_genotype[0]=current_genotype[0].replace("/","|")
                                if isinstance(likelihood,list):
                                    likelihood=str(','.join(current_genotype[1]))
                                else:
                                    likelihood=str(likelihood)
                                genotypes+=str(current_genotype[0])+":"+str(int(listcovUp[i])+int(listcovLow[i]))+":"+likelihood+":"+str(coverage)
                                if i<nbGeno-1 :
                                        genotypes+="\t" #Adds a \t except if this is the last genotype
                #Write results in VCF object
                VCFObject.formatField="GT:DP:PL:AD"
                VCFObject.genotypes=genotypes                                                                                                               
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
                                
        def FillVCF(self,VCFfile,nbGeno,table,VCFObject):
                """Take all necessary input variables to fill the vcf;  Fills the fields of the table which will be printed in the vcf ; return the table"""          
                if VCFObject.chrom=="*":
                        table[0]="."
                else:
                        table[0]=VCFObject.chrom
                table[1]=self.mappingPositionCouple
                table[2]=self.variantID
                table[3]=VCFObject.ref
                table[4]=self.CheckStrandAndReverseNucleotide(str(VCFObject.alt))
                table[5]="."
                table[6]=VCFObject.filterField
                table[7]="Ty="+str(VCFObject.variantType)+";"+"Rk="+str(self.rank)+";"+"UL="+str(self.unitigLeft)+";"+"UR="+str(self.unitigRight)+";"+"CL="+str(self.contigLeft)+";"+"CR="+str(self.contigRight)+";"+"Genome="+str(VCFObject.nucleoRef)+";"+"Sd="+str(VCFObject.reverse)
                table[7]=table[7].replace("None",".")
                table[7]=table[7].replace("none",".")
                table[7]=table[7].replace("=;","=.;")
                table[8]=VCFObject.formatField
                table[9]=VCFObject.genotypes
                VCFObject.PrintOneLine(table,VCFfile)#Print the line into the VCF
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
                                
        def WhichPathIsTheRef(self,VCFObject):
                """Finds which path is identical to the reference genome and defines it as the ref : specific method for each type of variant"""       
                #Checks the exception : different mapping position or both paths identical to the reference 
                if ((int(self.upper_path.mappingPosition)>0 and int(self.lower_path.mappingPosition)>0) and int(self.upper_path.mappingPosition)!=int(self.lower_path.mappingPosition)>0) or (self.upper_path.boolRef==False and self.lower_path.boolRef==False) or (self.upper_path.boolRef==True and self.lower_path.boolRef==True):
                        self.MismatchChecker()
                                          
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
        def GetMappingPositionCouple(self): #Validation SNP second part (specific method for close snps)
               """Defines the mapping position for the couple of variant by checking boolRef"""
               #for INDEL and simple snp
               if self.upper_path.boolRef==True:
                       self.mappingPositionCouple=int(self.upper_path.mappingPosition)+int(self.upper_path.correctedPos[0])+int(self.mappingPositionCouple)-1                       
               else:
                       self.mappingPositionCouple=int(self.lower_path.mappingPosition)+int(self.lower_path.correctedPos[0])+int(self.mappingPositionCouple)-1
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
        def CheckStrandAndReverseNucleotide(self,nucleo):
                """Reverse the alt nucleotide if it is needed"""
                if self.upper_path.boolRef==True:#Checks if the upper path is the reference
                        if self.upper_path.boolReverse==self.lower_path.boolReverse :#if the mapping strand is the same on both path => returns the nucleotide
                                return nucleo
                        elif int(self.upper_path.boolReverse)==1 and self.lower_path.boolReverse==".":
                                return nucleo 
                        elif self.upper_path.boolReverse!=self.lower_path.boolReverse:#if the mapping strand is different on both path => returns the reverse nuclotide
                                return self.ReverseComplement(nucleo)
                elif self.lower_path.boolRef==True:#Checks if the lower path is the reference
                        if self.upper_path.boolReverse==self.lower_path.boolReverse or (self.lower_path.boolReverse==1 and self.upper_path.boolReverse=="."):#if the mapping strand is the same on both path => returns the nucleotide
                                return nucleo
                        elif int(self.lower_path.boolReverse)==1 and self.upper_path.boolReverse==".":
                                return nucleo
                        elif self.upper_path.boolReverse!=self.lower_path.boolReverse:#if the mapping strand is different on both path => returns the reverse nuclotide
                                return self.ReverseComplement(nucleo)
                else :
                        return nucleo 
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
        def  CheckCoupleVariantID(self):
                """Test if the couple of paths has the same ID"""
                IDVariantUp=self.upper_path.listSam[0].split("_")[3]
                IDVariantLow= self.lower_path.listSam[0].split("_")[3]
                if IDVariantUp != IDVariantLow:
                        print "WARNING two consecutive lines do not store the same variant id: "
                        print self.upper_path.listSam
                        print self.lower_path.listSam
                        return 1
                else:
                        return 0                                                                           
#############################################################################################
#############################################################################################
class PATH():
        """corresponds to one path"""
        def __init__(self,line):
                self.listCoverage=[]#list of all the coverage by sample for the path
                self.dicoMappingPos={}#dictionnary with all the mapping positions associated with their number of mismatches with the reference
                self.listNucleotideReverse=[]#list of all the variant (snp) of the path on the reverse strand
                self.listNucleotideForward=[]#list of all the variant (snp) of the path on the forward strand                
                self.boolReverse=None#Boolean to know if the strand is reverse(-1) or forward(1)
                self.posMut=None#MD tag of the samfile "MD:Z:5A10A0A25G17" =>  5A10A0A25G17
                self.cigarcode=None#cigarcode of the samfile "61M"
                self.boolRef=None#Boolean to know if the path is identical to the reference
                self.nucleoRef=None #Nucleotide corresponding to the variant on the reference
                self.nucleo=None #nucleotide corresponding of the variant on the path
                self.listPosVariantOnPathToKeep=[]#list of the positions of all the variant on the in case of Reverse or Forward mapped path
                self.listPosReverse=[]#mapping position(s) of the variant on the path (if it is mapped on the reverse strand)
                self.listPosForward=[]#mapping position(s) of the variant on the path (if it is mapped on the forward strand)
                self.correctedPos=0 #list or position of the mapping variant by taking into account the shift with the reference
                if ">" not in line:# Case of samfile
                        self.listSam=line.rstrip('\r').rstrip('\n').split('\t')
                        self.discoName=self.listSam[0]
                        self.seq=self.listSam[9]#gets the sequence of the path
                        self.mappingPosition=abs(int(self.listSam[3])) #mapping position of the path
                        self.GetDicoMappingPosition()
                        self.CheckBitwiseFlag()
                else:#Mode ghost fastafile
                       line=line.strip('>').split("\n")
                       line.pop()
                       self.listSam=line#gets the sequence of the path
                       self.discoName=self.listSam[0]
                       self.seq=""
                       self.mappingPosition=0#mapping position of the path
                
                
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                     
        def GetSeq(self,seq):
                """Getter for sequence"""
                self.seq=seq        
        def GetDicoMappingPosition(self):
                """Retrieves for each path alignment information in a list ; retrieves a dictionary with all the positions of a path and the number of associated mismatch"""
                variant=self.listSam
                listXA=None
                strXA=None
                position=None
                nbMismatch=None
                #Error list with mapping positions very close to the first position given by bwa
                listerreur=set([(int(variant[3])-1),(int(variant[3])+1),(int(variant[3])+2),(int(variant[3])+3),(int(variant[3])-3),(int(variant[3])-2),int(variant[3])])
                #Creation of a dict with mapping position associated with number of mismatch
                if 'XA:Z' in ''.join(variant): # XA: tag for multiple mapping : Checks if the upper path is multiple mapped
                        for item in variant:
                                if "XA" in item:
                                        i=0
                                        #Parsing XA tag
                                        listXA=item.split(';')
                                        strXA = ','.join(listXA)
                                        listXA = strXA.split(',')
                                        listXA.pop()
                                        position=listXA[1:] #position=[pos1,cigarcode1,number of mismatch1 , pos2,cigarcode2,number of mismatch2,...]
                        while i<len(position): #Runs through the list 4 by 4 to get all the positions 
                                if abs(int(position[i])) not in listerreur : #Checks if the position is not too close to the main one
                                        self.dicoMappingPos[abs(int(position[i]))]=int(position[i+2]) #the position is associated to the number of mismatch in a dictionary
                                i+=4
                if abs(int(variant[3]))>0:#adds the main mapping position to the dictionary of all mapping positions
                      posMut,nbMismatch=self.GetTag()
                      self.dicoMappingPos[abs(int(variant[3]))]=int(nbMismatch)
#---------------------------------------------------------------------------------------------------------------------------
#data=str(bin(int(FLAG SAM)))[::-1]
#bit = field to test
#0   read paired
#1   read mapped in proper pair
#2   read unmapped
#3   mate unmapped
#4   read reverse strand
#5   mate reverse strand
#6   first in pair
#7   second in pair
#8   not primary alignment
#9   read fails platform/vendor quality checks
#10  read is PCR or optical duplicate
#11  supplementary alignment
#
#---------------------------------------------------------------------------------------------------------------------------                                                                   
                                                                                                                  
        def CheckBitwiseFlag(self):
                """Checks if the BitwiseFlag contains the tested value such as : read reverse strand, read unmmaped and so on."""
                try:
                        data=str(bin(int(self.listSam[1])))[::-1]
                except ValueError:
                        self.listPosVariantOnPathToKeep=self.listPosForward
                        self.boolReverse="1"
                        return 
                try:
                        if (data[4]=='1'):
                            self.boolReverse="-1"
                            self.listPosVariantOnPathToKeep=self.listPosReverse
                            return
                except IndexError:
                        self.listPosVariantOnPathToKeep=self.listPosForward
                        self.boolReverse="1"
                        return         
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------          
        def CigarcodeChecker(self):
                """Checks in the cigarcode of the samfile if there is a shift in the alignment between the path and the reference"""
                cigarcode=self.listSam[5]               
                parsingCigarCode=re.findall('(\d+|[A-Za-z])',cigarcode) #ParsingCigarCode=['2', 'S', '3', 'M', '1', 'I', '25', 'M']
                listPosRef=[]
                listShift=[]
                somme=0
                shift=0
                pos=0
                i=1
                j=0
                listpol=self.listPosVariantOnPathToKeep
                while i<len(parsingCigarCode):#Goes through the list by twos to get all the letters and to take them into account
                        if parsingCigarCode[i]=="S":
                                shift-=int(parsingCigarCode[i-1])
                                pos+=int(parsingCigarCode[i-1])
                        elif parsingCigarCode[i]=="M":
                                pos+=int(parsingCigarCode[i-1])
                        elif parsingCigarCode[i]=="D":
                                shift+=int(parsingCigarCode[i-1])
                        elif parsingCigarCode[i]=="I":
                                shift-=int(parsingCigarCode[i-1])#There is a nucleotide of shift compared to the reference
                                pos+=int(parsingCigarCode[i-1]) #We advance in the query SEQ
                        #Hard clipping (clipped sequences NOT present in SEQ)
                        elif parsingCigarCode[i]=="H":
                                shift-=int(parsingCigarCode[i-1]) # It's the shift in the alignment between the reference and the sequence of the variant 
                                pos+=int(parsingCigarCode[i-1])
                        #Padding (silent deletion from padded reference)
                        elif parsingCigarCode[i]=="P":
                                shift+=int(parsingCigarCode[i-1])
                                pos+=int(parsingCigarCode[i-1])
                        elif parsingCigarCode[i]=="=":
                                pos+=int(parsingCigarCode[i-1])
                        elif parsingCigarCode[i]=="X":
                                pos+=int(parsingCigarCode[i-1])
                        if len(listpol)==1:#Simple SNP and INDEL
                                if pos>=int(listpol[0]):
                                        posRef=int(listpol[0])+shift#takes into account the shift to add the after the mapping position and the variant position in the sequence                                
                                        listShift.append(shift)
                                        listPosRef.append(posRef)
                                        return(listPosRef,listShift)
                        elif len(listpol)>1:#Close SNPs
                                while int(pos)>=int(listpol[j]):#Goes through the list of position (close snps) and see if the position is affected by the shift (means shift before the position)self.listNucleotideForward
                                        posRef=int(listpol[j])+shift #Add the shift to the position (to get the real position of the snp on the reference)
                                        listPosRef.append(posRef) #Add the position to the list by taking into account the shift only if the current position 
                                        listShift.append(shift)
                                        if j<(len(listpol)-1):
                                                j+=1
                                        else:
                                                return(listPosRef,listShift)
                        i+=2                
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                               
        def ReferenceChecker(self,shift,posCentraleRef,VCFObject):
                """Function which allows to get the MD tag parsing; checks if path nucleotide is identical to the reference nucleotide"""
                i=0
                posMut,nbMismatch=self.GetTag()
                boolDel=True
                pos=shift
                nucleoRef=None
                boolEgalRef=None
                matchInt=None
                parsingPosMut=re.findall('(\d+|[A-Za-z]|\^)',posMut)
                while i<len(parsingPosMut):#Converts the number into integer 
                        matchInt=re.match(r'\d+',parsingPosMut[i]) #Integer motif
                        if matchInt:
                                parsingPosMut[i]=int(parsingPosMut[i])
                        i+=1
                i=0
                while i<len(parsingPosMut): #Goes through the list to know if the variant is identical to the reference
                        if isinstance(parsingPosMut[i],int): #Checks if it's a number of nucleotide or a letter
                                pos+=parsingPosMut[i] #Adds to pos the current number of the list
                        elif parsingPosMut[i]=="^":#In case of deletion from the reference we have to substract the deletion from the current position  
                                i+=1
                                while boolDel: #Checks if it is still a letter in the deletion to substract it from the current position
                                        if isinstance(parsingPosMut[i],int): #If it is an integer we achieved to take into account the deletion : adds the integer to the current position
                                                boolDel=False
                                                pos+=parsingPosMut[i]
                                        else:
                                                pos-=1 #Substracts the nucleotide from the current position
                                                i+=1
                                boolDel=True
                        else:
                                pos+=1
                        if pos==posCentraleRef: # Checks if the current position pos is identical to the position of the variant 
                                if isinstance(parsingPosMut[i],str): #=> it means that the nucleotide is different in the variant and in the reference
                                        self.boolRef=False
                                        self.nucleoRef=parsingPosMut[i]
                                else: #If the last item of the list of the MD tag is an intger => it means that the nucleotide of the allele is identical to the reference
                                        self.boolRef=True
                                break
                        if pos>posCentraleRef: #If the current position is bigger than the variant position it means that the nucleotide of the variant is identical to the reference
                                self.boolRef=True
                                break
                        i+=1
                
                VCFObject.nucleoRef=nucleoRef  
    # boolEgalRef : boolean if TRUE the nucleotide in the variant is equal to the reference
    # nucleoRef : if the nucleotide is different from the reference return the nucleotide of reference
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                         
        def GetCoverage(self):
                """Gets the coverage by path in the discosnp++ header"""
                for item in self.listSam[0].split('|'): 
                        if "C" in item:
                                matchC=re.match(r'^C',item)
                                if matchC:
                                        self.listCoverage.append(item.split('_')[1])    
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                             
        def GetTag(self):
                """Gets the number of mismatch in the samline"""
                for field in self.listSam:
                        if "MD" in field:
                                posMut = field.split(":")[2] #MD tag parsing
                        if "NM" in field:
                                nbMismatch=field.split(":")[2]#Gets the number of mismatch for the first position given by bwa
                return posMut,nbMismatch               
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                             
                        
        def CheckPosVariantFromRef(self,VCFObject): #Validation snp first part
                """Checks if the variant is identical to the reference or not ; defines the nucleotide on the reference"""
                dicoClose={}
                nucleo=None
                boolRef=None
                nucleoRef=None
                if int(self.mappingPosition)>0:
                        #Gets the shift by positions (insertion,deletion,sofclipping) and update of the position on the path
                        listCorrectedPos,listShift=self.CigarcodeChecker()
                        self.correctedPos=listCorrectedPos
                        #Defines if the path is identical to the reference and what is the nucleotide on the reference
                        for i in range(len(listCorrectedPos)):#Loops on the list of corrected positions
                                self.ReferenceChecker(listShift[i],listCorrectedPos[i],VCFObject)#Checks if the path is identical to the reference genome
                                if int(self.boolReverse)==1 and self.listNucleotideForward!=[]:#If we are on the forward strand => defines the nucleotide for the current snp or indel.
                                        self.nucleo=self.listNucleotideForward[i]
                                        if self.nucleoRef==None:#If there is no reference nucleotide given by ReferenceChecker, it means that the variant is equal to the reference so we defined it !
                                                self.nucleoRef=self.listNucleotideForward[i]
                                elif int(self.boolReverse)==-1 and self.listNucleotideReverse!=[]:#If we are on the reverse strand => defines the nucleotide for the current snp or indel.
                                        self.nucleo=self.listNucleotideReverse[i]
                                        if self.nucleoRef==None:#If there is no reference nucleotide given by ReferenceChecker, it means that the variant is equal to the reference so we defined it !
                                                self.nucleoRef=self.listNucleotideReverse[i]
                                dicoClose[self.listPosVariantOnPathToKeep[i]]=[(self.boolRef),(self.nucleoRef),(listCorrectedPos[i]),(self.nucleo),(self.boolReverse),(int(listCorrectedPos[i])+int(self.mappingPosition))]#Fills the dictionary to keep all informations for close snps
                                if i==0: #Keeps the information of the first snp/indel to fill the attributs of the path object
                                      boolRef=self.boolRef
                                      nucleoRef=self.nucleoRef
                                      nucleo=self.nucleo
                                self.nucleoRef=None#Resets the reference nucleotide for the next snp (case of close snps)
                                                                                                                                                                                                          
                elif int(self.mappingPosition)<=0:#Case of unmapped path                     
                        listCorrectedPos=self.listPosForward#We keep the forward position for every snps/indel on the path
                        self.listPosVariantOnPathToKeep=self.listPosForward
                        shift=None#There is no shift with the reference
                        self.boolReverse="."
                        self.nucleoRef="."
                        self.boolRef=False
                        self.correctedPos=listCorrectedPos
                        if self.listNucleotideForward!=[]:
                                self.nucleo=self.listNucleotideForward[0]
                                for i in range(len(self.listNucleotideForward)):#Loops on the list of position to fill the dictionary for close snps
                                        dicoClose[self.listPosForward[i]]=[(self.boolRef),(self.nucleoRef),(listCorrectedPos[i]),(self.listNucleotideForward[i]),self.boolReverse,(int(listCorrectedPos[i])+int(self.mappingPosition))]
                                        if i==0:
                                                boolRef=self.boolRef
                                                nucleoRef=self.nucleoRef
                                                nucleo=self.nucleo
                
                #Fills the attribut of the path with the information of the first snp/indel        
                self.boolRef=boolRef
                self.nucleoRef=nucleoRef
                self.nucleo=nucleo
                return(dicoClose)                                                                           
#############################################################################################
#############################################################################################
class SNP(VARIANT):
        def __init__(self,line1,line2):
                VARIANT.__init__(self,line1,line2)
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                     
        def WhichPathIsTheRef(self,VCFObject):
                VARIANT.WhichPathIsTheRef(self,VCFObject)                
                posUnmapped=self.CheckContigUnitig(self.unitigLeft,self.contigLeft) #Takes into account the lenght of the unitig/contig for the position of unmapped allele (position of the allele on the lower path)
#---------------------------------------------------------------------------------------------------------------------------
##Case : two mapped paths
                if int(self.upper_path.mappingPosition)>0 and int(self.lower_path.mappingPosition)>0:
                        ##The path identical to the reference is the lower path 
                        if self.lower_path.boolRef==True and self.upper_path.boolRef==False:
                                VCFObject.chrom=self.lower_path.listSam[2]
                                VCFObject.ref=self.lower_path.nucleo
                                VCFObject.alt=self.upper_path.nucleo
                                VCFObject.reverse=self.lower_path.boolReverse
                                VCFObject.nucleoRef=self.lower_path.nucleoRef
                        ##The path identical to the reference is the upper path 
                        elif self.upper_path.boolRef==True and self.lower_path.boolRef==False:
                                VCFObject.chrom=self.upper_path.listSam[2]
                                VCFObject.ref=self.upper_path.nucleo
                                VCFObject.alt=self.lower_path.nucleo
                                VCFObject.reverse=self.upper_path.boolReverse
                                VCFObject.nucleoRef=self.upper_path.nucleoRef
                        ##No path is identical to the reference => lexicographique choice
                        elif self.upper_path.boolRef==False and self.lower_path.boolRef==False:
                                if  self.upper_path.nucleo< self.lower_path.nucleo:
                                        VCFObject.chrom=self.upper_path.listSam[2]
                                        VCFObject.ref=self.upper_path.nucleo
                                        VCFObject.alt=self.lower_path.nucleo
                                        VCFObject.reverse=self.upper_path.boolReverse
                                        VCFObject.nucleoRef=self.upper_path.nucleoRef
                                elif  self.upper_path.nucleo> self.lower_path.nucleo:
                                        VCFObject.chrom=self.lower_path.listSam[2]
                                        VCFObject.ref=self.lower_path.nucleo
                                        VCFObject.alt=self.upper_path.nucleo
                                        VCFObject.reverse=self.lower_path.boolReverse
                                        VCFObject.nucleoRef=self.lower_path.nucleoRef
                      
#---------------------------------------------------------------------------------------------------------------------------
##Case : Lower path mapped and upper path unmapped      
                elif int(self.upper_path.mappingPosition)<=0 and int(self.lower_path.mappingPosition)>0:
                        VCFObject.chrom=self.lower_path.listSam[2]
                        VCFObject.ref=self.lower_path.nucleo
                        VCFObject.alt=self.upper_path.nucleo
                        VCFObject.reverse=self.lower_path.boolReverse
                        VCFObject.nucleoRef=self.lower_path.nucleoRef
#---------------------------------------------------------------------------------------------------------------------------
##Case : Upper path mapped and lower path unmapped        
                elif int(self.upper_path.mappingPosition)>0 and int(self.lower_path.mappingPosition)<=0:
                        VCFObject.chrom=self.upper_path.listSam[2]
                        VCFObject.ref=self.upper_path.nucleo
                        VCFObject.alt=self.lower_path.nucleo
                        VCFObject.reverse=self.upper_path.boolReverse
                        VCFObject.nucleoRef=self.upper_path.nucleoRef
#---------------------------------------------------------------------------------------------------------------------------
##Case : Both paths are unmapped       
                elif int(self.upper_path.mappingPosition)<=0 and int(self.lower_path.mappingPosition)<=0:
                        if  self.lower_path.nucleo<self.upper_path.nucleo:
                                VCFObject.chrom=self.lower_path.discoName.split("|")[0]
                                VCFObject.ref=self.lower_path.nucleo
                                VCFObject.alt=self.upper_path.nucleo
                                VCFObject.reverse=self.lower_path.boolReverse
                                VCFObject.nucleoRef=self.lower_path.nucleoRef
                                self.mappingPositionCouple=int(posUnmapped)
                        else:
                                VCFObject.chrom=self.upper_path.discoName.split("|")[0]
                                VCFObject.ref=self.upper_path.nucleo
                                VCFObject.alt=self.lower_path.nucleo
                                VCFObject.reverse=self.upper_path.boolReverse
                                VCFObject.nucleoRef=self.upper_path.nucleoRef
                                self.mappingPositionCouple=int(posUnmapped)                            
#############################################################################################
#############################################################################################
class INDEL(VARIANT):
        def __init__(self,line1,line2):
                VARIANT.__init__(self,line1,line2)
                self.insert=None
                self.nucleotideStart=None   
                self.smallestSequence=None
                self.longestSequence=None
                self.ambiguityPos=None
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                     
        def GetPolymorphismFromHeader(self):
                #Test which is the samllest sequence
                if len(self.upper_path.seq)<len(self.lower_path.seq):
                        self.smallestSequence=self.upper_path.seq
                        self.longestSequence=self.lower_path.seq
                else:
                       self.smallestSequence=self.lower_path.seq
                       self.longestSequence=self.upper_path.seq
                for key,(posD,ind,amb) in self.dicoAllele.items():#Goes through the dictionary of parsed header
                        self.upper_path.listPosForward.append(int(posD)+1)
                        self.lower_path.listPosForward.append(int(posD)+1)
                        self.lower_path.listPosReverse.append(len(self.smallestSequence)-int(posD))
                        self.upper_path.listPosReverse.append(len(self.smallestSequence)-int(posD))
                        self.insert=self.longestSequence[int(posD)-1:(int(posD)+int(ind))]
                        self.ntStart=self.longestSequence[(int(posD)-1)]
                        self.ambiguityPos=amb
                        self.lower_path.nucleo="."
                        self.upper_path.nucleo="."
                        
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                                          
        def WhichPathIsTheRef(self,VCFObject):
                VARIANT.WhichPathIsTheRef(self,VCFObject)
                posUnmapped=self.CheckContigUnitig(self.unitigLeft,self.contigLeft) #Takes into account the lenght of the unitig/contig for the position of unmapped allele (position of the allele on the lower path)
            #Checks if the insert correpond to the upper path or to the lower path
                if len(self.upper_path.seq)<len(self.lower_path.seq):
                        self.lower_path.nucleo=self.insert
                        self.upper_path.nucleo=self.ntStart
                else:
                        self.upper_path.nucleo=self.insert
                        self.lower_path.nucleo=self.ntStart
                if  int(self.upper_path.mappingPosition)>0 and int(self.lower_path.mappingPosition)<=0:
                        self.upper_path.boolRef=True
                        self.lower_path.boolRef=False
                elif int(self.upper_path.mappingPosition)<=0 and int(self.lower_path.mappingPosition)>0:
                        self.upper_path.boolRef=False
                        self.lower_path.boolRef=True              
            ##Fills the VCF if the upper path is considered as the reference
                if self.upper_path.boolRef==True:
                        if len(self.upper_path.nucleo)==len(self.insert):
                                self.upper_path.nucleoRef="."
                                VCFObject.variantType="INS"
                        else:
                                self.upper_path.nucleoRef="."
                                VCFObject.variantType="DEL"
                        try:
                                VCFObject.chrom=self.upper_path.listSam[2]
                        except IndexError:
                                VCFObject.chrom=self.upper_path.listSam[0].split("|")[0]    
                        VCFObject.ref=self.upper_path.nucleo
                        VCFObject.alt=self.lower_path.nucleo
                        VCFObject.reverse=self.upper_path.boolReverse
                        VCFObject.nucleoRef=self.lower_path.nucleoRef
                elif self.lower_path.boolRef==True:
                        if len(self.lower_path.nucleo)==len(self.insert):
                                self.lower_path.nucleoRef="."
                                VCFObject.variantType="INS"
                        else:
                                self.lower_path.nucleoRef="."
                                VCFObject.variantType="DEL"
                        try:
                                VCFObject.chrom=self.lower_path.listSam[2]
                        except IndexError:
                                VCFObject.chrom=self.lower_path.listSam[0].split("|")[0]  
                        VCFObject.ref=self.lower_path.nucleo
                        VCFObject.alt=self.upper_path.nucleo
                        VCFObject.reverse=self.lower_path.boolReverse
                        VCFObject.nucleoRef=self.lower_path.nucleoRef
                if int(self.upper_path.mappingPosition)<=0 and int(self.lower_path.mappingPosition)<=0:
                        if self.lower_path.boolRef==True:
                                self.mappingPositionCouple=int(posUnmapped)
                        else:
                                self.mappingPositionCouple=int(posUnmapped)
                        if len(self.upper_path.nucleo)==len(self.insert):
                                VCFObject.chrom=self.upper_path.discoName.split("|")[0]
                                self.upper_path.boolRef=True
                                self.upper_path.nucleoRef="."
                                VCFObject.variantType="INS"
                                VCFObject.ref=self.upper_path.nucleo
                                VCFObject.alt=self.lower_path.nucleo
                                VCFObject.reverse=self.upper_path.boolReverse
                                VCFObject.nucleoRef=self.lower_path.nucleoRef
                        else:
                                VCFObject.chrom=self.lower_path.discoName.split("|")[0]
                                self.upper_path.boolRef=False
                                self.upper_path.nucleoRef="."
                                VCFObject.variantType="DEL"
                                VCFObject.ref=self.lower_path.nucleo
                                VCFObject.alt=self.upper_path.nucleo
                                VCFObject.reverse=self.lower_path.boolReverse
                                VCFObject.nucleoRef=self.lower_path.nucleoRef
    
                                                                          
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                          
        def GetMappingPositionCouple(self):
                VARIANT.GetMappingPositionCouple(self)
                self.mappingPositionCouple=int(self.mappingPositionCouple)-int(self.ambiguityPos)-1                                            
#############################################################################################
#############################################################################################
class SNPSCLOSE(VARIANT):
        def __init__(self,line1,line2):
                VARIANT.__init__(self,line1,line2)        
                self.dicoCloseSNPUp={} #dictionnary with all the informations for close snps : boolean to know if the allele is identical to the reference,position on the variant, reverse nucleotide for the allele, if the path is reverse or not, mapping position
                self.dicoCloseSNPLow={}
                
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                   
        def GetDicoClose(self,dicoCloseUp,dicoCloseLow):# Gets the outputs of the method CheckPosVariantFromRef (PATH CLASS)
                self.dicoCloseSNPUp=dicoCloseUp
                self.dicoCloseSNPLow=dicoCloseLow               
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                                                                        
                       
        def WhichPathIsTheRef(self,VCFObject):
                VARIANT.WhichPathIsTheRef(self,VCFObject)
                VCFObject.phased=True 
                table = [0] * 10 #Create a 10 cols array
                tablebis=[]
                posUnmapped=self.CheckContigUnitig(self.unitigLeft,self.contigLeft)
                listPositionPolymorphismeOnPathUp=self.upper_path.listPosVariantOnPathToKeep
                listPositionPolymorphismeOnPathLow=self.lower_path.listPosVariantOnPathToKeep
                VCFObject.nucleoRef=[]
##Case : two mapped paths
                if int(self.upper_path.mappingPosition)>0 and int(self.lower_path.mappingPosition)>0:
                        
                        ##Sorts the list of position to get the smallest one and its position in the list unsorted!
                        ##Keeps the close snps to sort them : indeed all the lists and dictionnaries :listnucleoUp,listPositionPolymorphismeOnPathUp,listPositionPolymorphismeOnPathLow,listnucleoLow self.dicoCloseSNPUp,self.dicoCloseSNPLow are classified according to dicoHeader so if we start by sorting we lose the correspondence between data
                        listSortedPosUp=list(listPositionPolymorphismeOnPathUp)
                        listSortedPosUp.sort()
                        indexSmallestPosUp=listPositionPolymorphismeOnPathUp.index(listSortedPosUp[0])
                        listSortedPosLow=list(listPositionPolymorphismeOnPathLow)
                        listSortedPosLow.sort()
                        indexSmallestPosLow=listPositionPolymorphismeOnPathLow.index(listSortedPosLow[0])
                        self.upper_path.boolRef=self.dicoCloseSNPUp[listPositionPolymorphismeOnPathUp[indexSmallestPosUp]][0]
                        self.lower_path.boolRef=self.dicoCloseSNPLow[listPositionPolymorphismeOnPathLow[indexSmallestPosLow]][0]
                        #self.upper_path.boolRef=self.dicoCloseSNPUp[listPositionPolymorphismeOnPathUp[indexSmallestPosUp]][0]
                        #self.lower_path.boolRef=self.dicoCloseSNPLow[listPositionPolymorphismeOnPathLow[indexSmallestPosLow]][0]
                        #Decides what is the smallest position according to the reference path (useful if the paths are not aligned on the same strand)
                        if (self.upper_path.boolRef==False and self.lower_path.boolRef==False) or (self.upper_path.boolRef==True and self.lower_path.boolRef==True):
                                VARIANT.MismatchChecker(self)
                        if self.upper_path.boolRef==True and self.lower_path.boolRef==False: #The smallest position identical to the reference is on the upper path
                                indexSmallestPos=indexSmallestPosUp
                                listPolymorphismPos=listPositionPolymorphismeOnPathUp
                        elif self.lower_path.boolRef==True and self.upper_path.boolRef==False:#The smallest position identical to the reference is on the lower path
                                indexSmallestPos=indexSmallestPosLow
                                listPolymorphismPos=listPositionPolymorphismeOnPathLow
                        elif self.upper_path.boolRef==False and self.lower_path.boolRef==False: #Both paths are different from the reference => choice with the lexicographical order
                                if self.upper_path.nucleo<self.lower_path.nucleo:
                                        indexSmallestPos=indexSmallestPosUp
                                        listPolymorphismPos=listPositionPolymorphismeOnPathUp
                                else:
                                        indexSmallestPos=indexSmallestPosLow
                                        listPolymorphismPos=listPositionPolymorphismeOnPathLow
                        #dicoClose[self.listPosVariantOnPathToKeep[i]]=[self.boolRef,self.nucleoRef,correctedPos[i],nucleo,self.boolReverse,(int(correctedPos[i])+int(self.mappingPosition))]
                        for comptPol in range(len(listPolymorphismPos)): #Goes through the list of the variant position starting with the smallest
                            
                            positionSnpUp=self.dicoCloseSNPUp[listPositionPolymorphismeOnPathUp[comptPol]][5]
                            positionSnpLow=self.dicoCloseSNPLow[listPositionPolymorphismeOnPathLow[comptPol]][5]
                            nucleoUp=self.dicoCloseSNPUp[listPositionPolymorphismeOnPathUp[comptPol]][3]
                            nucleoRefUp=self.dicoCloseSNPUp[listPositionPolymorphismeOnPathUp[comptPol]][1]
                            nucleoLow=self.dicoCloseSNPLow[listPositionPolymorphismeOnPathLow[comptPol]][3]
                            nucleoRefLow=self.dicoCloseSNPLow[listPositionPolymorphismeOnPathLow[comptPol]][1]
                            #Fills the variable table with the vcf fields ; Checks the "REF" path to fill the vcf
                            if self.lower_path.boolRef==True and self.upper_path.boolRef==False: #The lower path is defined as REF
                            #table[1]=self.mappingPositionCouple
                            #table[3]=self.ref
                            #table[4]=self.alt
                               
                                VCFObject.chrom=self.lower_path.listSam[2]
                                table[1]=int(positionSnpLow)-1
                                table[3]=nucleoLow
                                table[4]=self.CheckStrandAndReverseNucleotide(nucleoUp)
                                VCFObject.nucleoRef.append([nucleoRefLow,positionSnpLow])
                                VCFObject.reverse=self.lower_path.boolReverse   
                            elif self.upper_path.boolRef==True and self.lower_path.boolRef==False:#The upper path is defined as REF
                                table[1]=int(positionSnpUp)-1
                                table[3]=nucleoUp
                                table[4]=self.CheckStrandAndReverseNucleotide(nucleoLow)
                                VCFObject.nucleoRef.append([nucleoRefUp,positionSnpUp])
                                VCFObject.chrom=self.upper_path.listSam[2]
                                VCFObject.reverse=self.upper_path.boolReverse                                
                            tablebis.append(list(table))#Stocks the variable with all the vcf fields for each close snp to sort it and print it in the vcf
                        tablebis=sorted(tablebis, key=lambda colonnes: colonnes[1])
                        return tablebis
#---------------------------------------------------------------------------------------------------------------------------
##Case : Both paths are unmapped     
                elif int(self.upper_path.mappingPosition) <= 0 and int(self.lower_path.mappingPosition)<= 0:
                        self.upper_path.boolReverse="."
                        i=0
                        for i in range(len(listPositionPolymorphismeOnPathUp)):
                                VCFObject.chrom=self.upper_path.discoName.split("|")[0]
                                positionSnpUp=int(listPositionPolymorphismeOnPathUp[i])+int(posUnmapped)
                                positionSnpLow=int(listPositionPolymorphismeOnPathUp[i])+int(posUnmapped)
                                nucleoUp=self.upper_path.listNucleotideForward[i]
                                nucleoRefUp="."
                                nucleoLow=self.lower_path.listNucleotideForward[i]
                                nucleoRefLow="."
                                VCFObject.reverse="."
                                table[1]=positionSnpUp
                                table[3]=nucleoUp
                                table[4]=nucleoLow
                                VCFObject.nucleoRef.append([nucleoRefUp,positionSnpUp])
                                tablebis.append(list(table))
                        tablebis=sorted(tablebis, key=lambda colonnes: colonnes[1])
                        return tablebis
#---------------------------------------------------------------------------------------------------------------------------
##Case : Upper path mapped and lower path unmapped  
                elif int(self.upper_path.mappingPosition)>0 and int(self.lower_path.mappingPosition)<=0:
                        comptPol=0
                        VCFObject.chrom=self.upper_path.listSam[2]
                        VCFObject.reverse=self.upper_path.boolReverse
                        for comptPol in range(len(listPositionPolymorphismeOnPathUp)):
                                if (int(self.upper_path.boolReverse)==-1):
                                        nucleoLow=self.ReverseComplement(self.lower_path.listNucleotideForward[comptPol])
                                        nucleoUp=self.upper_path.listNucleotideReverse[comptPol]
                                elif int(self.upper_path.boolReverse)==1:
                                        nucleoLow=self.lower_path.listNucleotideForward[comptPol]
                                        nucleoUp=self.upper_path.listNucleotideForward[comptPol]
                                nucleoRefLow="."
                                positionSnpUp=int(self.dicoCloseSNPUp[listPositionPolymorphismeOnPathUp[comptPol]][5])-1
                                nucleoRefUp=self.dicoCloseSNPUp[listPositionPolymorphismeOnPathUp[comptPol]][1]
                                table[1]=positionSnpUp
                                table[3]=nucleoUp
                                table[4]=nucleoLow
                                VCFObject.nucleoRef.append([nucleoRefUp,positionSnpUp])
                                tablebis.append(list(table))
                        tablebis=sorted(tablebis, key=lambda colonnes: colonnes[1])
                        return tablebis
#---------------------------------------------------------------------------------------------------------------------------
##Case : Lower path mapped and upper path unmapped            
                elif int(self.upper_path.mappingPosition)<=0 and int(self.lower_path.mappingPosition)>0:
                        VCFObject.chrom=self.lower_path.listSam[2]
                        VCFObject.reverse=self.lower_path.boolReverse
                        for comptPol in range(len(listPositionPolymorphismeOnPathLow)):
                                if (int(self.lower_path.boolReverse)==-1):
                                        nucleoUp=self.ReverseComplement(self.upper_path.listNucleotideForward[comptPol])
                                        nucleoLow=self.lower_path.listNucleotideReverse[comptPol]
                                elif int(self.lower_path.boolReverse)==1:
                                        nucleoUp=self.upper_path.listNucleotideForward[comptPol]
                                        nucleoLow=self.lower_path.listNucleotideForward[comptPol]
                                nucleoRefUp="."
                                positionSnpLow=int(self.dicoCloseSNPLow[listPositionPolymorphismeOnPathLow[comptPol]][5])-1
                                nucleoRefLow=self.dicoCloseSNPLow[listPositionPolymorphismeOnPathLow[comptPol]][1]
                                table[1]=positionSnpLow
                                table[3]=nucleoLow
                                table[4]=nucleoUp
                                VCFObject.nucleoRef.append([nucleoRefLow,positionSnpLow])
                                tablebis.append(list(table))
                        tablebis=sorted(tablebis, key=lambda colonnes: colonnes[1])
                        return tablebis
                                    
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------                        
         
        def FillVCF(self,VCFfile,nbGeno,table,VCFObject):
                """print the VCFFile for each line of close snps"""
                ID=1
                i=0
                nucleoRef=None
                for line in range(len(table)):
                        for i in range(len(VCFObject.nucleoRef)):
                                if table[line][1] in VCFObject.nucleoRef[i]:
                                        nucleoRef=VCFObject.nucleoRef[i][0]   
                        if VCFObject.chrom=="*":
                                table[line][0]=self.listSam[0].split("_")[0]
                        else:
                                table[line][0]=VCFObject.chrom
                        table[line][2]=str(self.variantID)+"_"+str(ID)
                        table[line][5]="."
                        table[line][6]=VCFObject.filterField
                        table[line][7]="Ty="+str(VCFObject.variantType)+";"+"Rk="+str(self.rank)+";"+"UL="+str(self.unitigLeft)+";"+"UR="+str(self.unitigRight)+";"+"CL="+str(self.contigLeft)+";"+"CR="+str(self.contigRight)+";"+"Genome="+str(nucleoRef)+";"+"Sd="+str(VCFObject.reverse)
                        table[line][7]=table[line][7].replace("None",".")
                        table[line][7]=table[line][7].replace("none",".")
                        table[line][7]=table[line][7].replace("=;","=.;")
                        table[line][8]=VCFObject.formatField
                        table[line][9]=VCFObject.genotypes
                        ID+=1
                        i+=1
                        
                for l in range(len(table)):
                        VCFObject.PrintOneLine(table[l],VCFfile)        
        
        
#############################################################################################
#############################################################################################        
class VCFFIELD():
        def __init__(self):
                ##VCF Fields
                self.filterField=None
                self.variantType=None
                self.phased=None #phased genotype
                self.formatField=None 
                self.genotypes="" #genotype field =>put it in the vcf
                self.chrom=""
                self.ref=""
                self.alt=""
                self.qual=""
                self.nucleoRef=None
                self.reverse=""
        def PrintOneLine(self,table,VCF):
                """Prints the line of the current SNP in the VCF file."""
                if table==[0, 0, 0, 0, 0, 0, 0, 0, 0, 0] or (table[0]==0 and table[1]==0 and table[3]==0 and table[4]==0):
                        return
                for i in range(len(table)):
                        element=table[i]
                        element=str(element).replace("None",".")
                        VCF.write((str(element)).strip())
                        if i<len(table)-1: VCF.write("\t")
                VCF.write('\n') 
                               