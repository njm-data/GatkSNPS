#!/usr/bin/env python3


##GATK SNPS script
#needs: bwa
#gatk
#samtools
#picard
##other notes

#assumes illumina data (line 32)

import argparse
import sys, os
import subprocess
import shutil

#command line options
parser = argparse.ArgumentParser(description= 'Script to get bwa mem -> GATK SNPS')
parser.add_argument("-i","--indv",
									type=str,
									help="Inividual name")

parser.add_argument("-m","--mreads",
									type=str,
									help="Merged pear reads")

parser.add_argument("-r","--reference",
									type=str,
									help="Reference fasta")

parser.add_argument("-s","--sequencer",
                                    type=str,
                                    default="illumina",
                                    help="from samtools: Read Group Platform")

parser.add_argument("-rn","--resolution",
                                    type=str,
                                    default="BP_RESOLUTION",
                                    help="Resolution of genotyping BP or GVCF (BP_RESOLUTION,GVCF) ")
                                    
parser.add_argument("-bm","--bigmem",
									action="store_true",
									help="sets jar Xmx memory to 75gb if True for INDELREALIGNER") 
									##if more space is needed go to line 111

parser.add_argument("-gl","--gatklocation",
									type=str,
									help="Location of /GenomeAnalysisTK.jar file with the .jar included")

parser.add_argument("-l","--leave",
									action="store_true",
									help="If you want the temp files, have flag")

args = parser.parse_args()
indv=args.indv
mreads=args.mreads
reference=args.reference
sequencer=args.sequencer
resolution=args.resolution

#early kills
if  mreads == None:
	print("Missing merged pear reads")
	quit()
if reference == None:
	print("Missing reference fasta")
	quit()
if indv == None:
	print("No Individual Sample name")
	quit()
if args.bigmem:
    if args.gatklocation == None:
        gatklocation = shutil.which("GATK")
        print("GATK IS LOCATED AT " + gatklocation)
    else:
        print("GATK IS LOCATED AT " + args.gatklocation)


#reference set up
command = "bwa index " + reference + " "
subprocess.call(command,shell=True)
command = "picard CreateSequenceDictionary R=" + reference
subprocess.call(command,shell=True)
command = "samtools faidx " + reference
subprocess.call(command,shell=True)

#bwa mem alignment
command = "bwa mem " + reference + " " + mreads + " > temp_mem.sam"
subprocess.call(command, shell=True)

#picard/samtools cleaning
command = "picard SortSam INPUT=temp_mem.sam OUTPUT=temp_sorted.sam SORT_ORDER=coordinate"
subprocess.call(command,shell=True)
command = "picard MarkDuplicatesWithMateCigar INPUT=temp_sorted.sam OUTPUT=temp_marked.sam METRICS_File=temp_metrics.txt"
subprocess.call(command,shell=True)
command = "samtools view -bS temp_marked.sam > temp_marked.bam"
subprocess.call(command, shell=True)
command = "picard AddOrReplaceReadGroups I=temp_marked.bam O=temp_wrg.bam Sort_Order=coordinate RGID=foo RGLB=bar RGPL="+sequencer +" RGSM="+ indv + " Create_Index=True RGPU=unit1"
subprocess.call(command,shell=True)



#GATK
command = "GenomeAnalysisTK -T RealignerTargetCreator -R " + reference+ " -I temp_wrg.bam -o realigner.intervals"
subprocess.call(command,shell=True)

if args.bigmem==True:
	print(("Using more memory for INDELREALIGNER"))
	print(("GATK location being used is "+ gatklocation + " should read like /home/njmello/.conda/envs/bio/opt/gatk-3.8/GenomeAnalysisTK.jar"))
	command = "java -Xmx75G -jar " + gatklocation + " -T IndelRealigner -R " + reference + " -targetIntervals realigner.intervals -I temp_wrg.bam -o temp_realigned.bam"
else:
	print(("Using default memory for INDELREALIGNER"))
	command = "GenomeAnalysisTK -T IndelRealigner -R " + reference + " -targetIntervals realigner.intervals -I temp_wrg.bam -o temp_realigned.bam"
	subprocess.call(command,shell=True)
	
command = "GenomeAnalysisTK -T HaplotypeCaller -R " + reference + " -I temp_realigned.bam -o " + indv +"_" + resolution + ".g.vcf -ERC " + resolution
    #default filters out mapqless than 20
subprocess.call(command,shell=True)

#Clean up
if args.leave:
	command = "rm temp_*"
	subprocess.call(command,shell=True)
else:
	print(("Leaving temp files in place"))
