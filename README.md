# GatkSNPS
Pipeline from GATK Best Practices to produce SNPs
https://www.broadinstitute.org/partnerships/education/broade/best-practices-variant-calling-gatk-1

Has been tested with Illumina data, RNASeq and Hybrid Enrichment/SeqCap.

python environment requires:
- GATK (works with version 3.8)
- BWA
- Samtools
- Picard

## bwa2gatk.py:
Takes merged reads (tested on PEAR merged reads) and aligns to a referene fasta. After aligning, does the necessary picard/samtools cleaning not explicitly mentioned in the GATK pipeline. Then goes through GATK commands (RealignerTargetCreator, IndelRealigner, and HaplotypeCaller).
### Assumpitons/defaults:
  - Assumes Illumina sequencer for Picard's AddOrReplaceReadGroups, change with -s (sequencer)
  - Assumes no extra mem is needed for IndelRealigner. If more data is needed, use -bm flag and list location of GenomeAnalysisTK.jar file with -gk
  - For HaplotypeCaller assumpes BP_RESOLUTION, to switch to GVCF, just use -rn GVCF
  - OUTPUT NAME IS SampleName_Resolution.g.vcf
  - removes all intermediary files, if any are desired use -l to leave them.
### REQUIRED INPUTS:
  - Individual sample name
  - Merged reads
  - Reference

## gatk_geno.py:
  Genotypes together list of individual sample .g.vcfs, and filters according to Margress et. al 2019. Can get SNPS and INDELS. GATK commands GenotypeGVCFs, SelectVariants, and VariantFiltration)
### Assumptions/defaults:
  - Default SNP and INDEL filters are: '"QD < 2.0 || FS > 60.0 || MQ < 40.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0"'
  - Default only does SNPs, if indels are required us "-i" for indels to be ran as well.
  - Default output is FINAL_SNPs.vcf (or FINAL_INDELs.vcf), can change with -o output flag
  - All intermediary files are kept by default
### REQUIRED INPUTS:
  - List of location to all .g.vcf files
  - Reference
  
