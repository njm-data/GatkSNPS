#!/usr/bin/env python

##GATK Genotyping script
#needs: gatk
#list w/ path to all samples to be genotyped
#default filter expression from Mark Margress (Margress et. al 2019) & correspondance 

import argparse
import sys, os
import subprocess

#command line options
parser = argparse.ArgumentParser(description = 'Script to get genotypes')

parser.add_argument("-r","--reference",
                                    type=str,
                                    help="Reference fasta")
parser.add_argument("-l","--samplelist",
									type=str,
									help="List of all .g.vcf file locations")
parser.add_argument("-o","--output",
									type=str,
									help="Output name w/ .vcf",
									default="FINAL")
parser.add_argument("-sf","--SNPfilters",
									type=str,
									help="filterExpression for VariantFiltration",
									default='"QD < 2.0 || FS > 60.0 || MQ < 40.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0"')
parser.add_argument("-i","--indels",
									action="store_true",
									help="Flag if you want INDELS as well as SNPS")
parser.add_argument("-idf","--INDELfilters",
									type=str,
									help="filterExpression for VariantFiltration",
									default='"QD < 2.0 || FS > 60.0 || MQ < 40.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0"')

args = parser.parse_args()
reference=args.reference
samplelist=args.samplelist
output=args.output
filters=args.SNPfilters
idfilters=args.INDELfilters

#build massive genotyping command

with open(samplelist, "r") as f:
	lines=f.readlines()
lines = [l.replace('\n', '') for l in lines]
print("This is the list of samples")
print(lines)

n=[]
for individuals in lines:
    print(individuals)
    n.append(" -V "+ individuals)

m = ''.join([str(item) for item in n])

command = "GenomeAnalysisTK -T GenotypeGVCFs -R " + reference + m + " -o All.vcf.gz"
subprocess.call(command,shell=True)

#variant filtrations SNPS
command = "GenomeAnalysisTK -T SelectVariants -R " + reference + " -V All.vcf.gz -selectType SNP -o temp_raw_snps.vcf"
subprocess.call(command,shell=True)

command = 'GenomeAnalysisTK -T VariantFiltration -R ' + reference + ' -V temp_raw_snps.vcf --filterExpression ' + filters +' --filterName "FILTER" -o temp_Mark_filtered_snps.vcf'
subprocess.call(command,shell=True)

#variant filtrations indels
if args.indels:
	command = "GenomeAnalysisTK -T SelectVariants -R " + reference + " -V All.vcf.gz -selectType INDEL -o temp_raw_indels.vcf"
	subprocess.call(command,shell=True)
	command = 'GenomeAnalysisTK -T VariantFiltration -R ' + reference + ' -V temp_raw_indels.vcf --filterExpression ' + idfilters +' --filterName "FILTER" -o temp_Mark_filtered_indels.vcf'
	subprocess.call(command,shell=True)
	command = "grep -E '^#|PASS' temp_Mark_filtered_indels.vcf > " + output + "_INDELs.vcf"
	subprocess.call(command,shell=True)
else:
	print("Not creating INDELS vcf")

#final print out
command = "grep -E '^#|PASS' temp_Mark_filtered_snps.vcf > " + output + "_SNPs.vcf"
subprocess.call(command,shell=True)


f.close()
