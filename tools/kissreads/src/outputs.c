/**
 * Copyright INRIA , contributors Peterlongo
 * pierre.peterlongo@inria.fr
 *
 *
 * This software is a computer program whose purpose is to detect the
 * presence of a sequence in a set of NGS reads, and to compute its average quality and coverage
 *
 * This software is governed by the CeCILL license under French law and
 * abiding by the rules of distribution of free software.  You can  use,
 * modify and/ or redistribute the software under the terms of the CeCILL
 * license as circulated by CEA, CNRS and INRIA at the following URL
 * "http://www.cecill.info".
 
 * As a counterpart to the access to the source code and  rights to copy,
 * modify and redistribute granted by the license, users are provided only
 * with a limited warranty  and the software's author,  the holder of the
 * economic rights,  and the successive licensors  have only  limited
 * liability.
 
 * In this respect, the user's attention is drawn to the risks associated
 * with loading,  using,  modifying and/or developing or reproducing the
 * software by the user in light of its specific status of free software,
 * that may mean  that it is complicated to manipulate,  and  that  also
 * therefore means  that it is reserved for developers  and  experienced
 * professionals having in-depth computer knowledge. Users are therefore
 * encouraged to load and test the software's suitability as regards their
 * requirements in conditions enabling the security of their systems and/or
 * data to be ensured and,  more generally, to use and operate it in the
 * same conditions as regards security.
 *
 * The fact that you are presently reading this means that you have had
 * knowledge of the CeCILL license and that you accept its terms.
 */

/*
 * outputs.c
 *
 *  Created on: 27 oct. 2010
 *      Author: ppeterlo
 */
#include <fragment_index.h>
#include <fragment_info.h>
#include <commons.h>
#include <string.h>
#include <tree.h>
#include <stdlib.h>
#include <limits.h>
#include <math.h>
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define ABS(a) (((a) < 0) ? -(a) : (a))

//#define DEBUG_QUALITY


#if !HAVE_LOG2F
#define log2f log
#endif

// Operation made on each data set (read_set_id)
//#define op() MIN(corrected_avg_lo[read_set_id],corrected_avg_up[read_set_id]) /	(corrected_avg_lo[read_set_id]+corrected_avg_up[read_set_id]);
#define op() corrected_avg_up[read_set_id] /	(corrected_avg_lo[read_set_id]+corrected_avg_up[read_set_id]);




float rank_max(const float * corrected_avg_up, const float * corrected_avg_lo, const int number_of_read_sets){
	int read_set_id;
	float rank=0;
	float temp;
	//	float sum=0;
	for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
		if(corrected_avg_lo[read_set_id]+corrected_avg_up[read_set_id]){ // not null in the 2 isoforms
			temp = op()
			if(temp > rank)
				rank = temp;
		}
	}
	return rank;
}

float rank_min(const float * corrected_avg_up, const float * corrected_avg_lo, const int number_of_read_sets){
	int read_set_id;
	float rank=INT_MAX;
	float temp;
	for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
		if(corrected_avg_lo[read_set_id]+corrected_avg_up[read_set_id]){ // not null in the 2 isoforms
			temp = op()
			if(temp < rank)
				rank = temp;
		}
	}
	return rank;
}

float rank_sum(const float * corrected_avg_up, const float * corrected_avg_lo, const int number_of_read_sets){
	int read_set_id;
	float rank=0;
	for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
		if(corrected_avg_lo[read_set_id]+corrected_avg_up[read_set_id]){ // not null in the 2 isoforms
			rank += op()
		}
	}
	return rank;
}

float rank_avg(const float * corrected_avg_up, const float * corrected_avg_lo, const int number_of_read_sets){
	return rank_sum(corrected_avg_up,corrected_avg_lo,number_of_read_sets)/(float)number_of_read_sets;
}

float rank_standard_deviation (const float * corrected_avg_up, const float * corrected_avg_lo, const int number_of_read_sets){
	float avg= rank_avg(corrected_avg_up,corrected_avg_lo,number_of_read_sets);
	float temp;
	float sdev=0.0;
	float sum=0.0;
	int read_set_id;
	for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
		if(corrected_avg_lo[read_set_id]+corrected_avg_up[read_set_id]){ // not null in the 2 isoforms
			temp=op()
			sum+=pow(temp-avg,2);
		}
	}
	sdev=sum/(number_of_read_sets-1);
	sdev = sqrt(sdev);
	return sdev;
}

/**
 * TODO: the entropy function raises some problems: any path having zero value creates a -inf value with the log of the fraction...
 */
float rank_entropy(const float * corrected_avg_up, const float * corrected_avg_lo, const int number_of_read_sets){
    int read_set_id;
	float ranksum=rank_sum(corrected_avg_up,corrected_avg_lo,number_of_read_sets);
	float temp;
	float entropy = 0.0;
	float fraction;
    //	printf("hey (sum =%f): ",ranksum);
	for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
        //		printf("(%f/%f) ", corrected_avg_lo[read_set_id], corrected_avg_up[read_set_id]);
		if(corrected_avg_lo[read_set_id]+corrected_avg_up[read_set_id]){ // not null in the 2 isoforms
			temp=op()
			fraction = temp/ranksum;
            //			printf("[fraction=%f] ",fraction);
			entropy -= (fraction * log2f (fraction));
		}
	}
    //	printf(" --> %f\n", entropy);
	return entropy;
}

/*Calculates the phi coefficient of 2*2 contingency table. Value close to 1 indicates an association between the alleles and the conditions.*/
/*Note that this value is valid if at least 3 out of the 4 values are non 0, or if the .Otherwise it output -1*/
float phi(int a,int b, int c,int d) {
    //  int denom=(a+b)*(c+d)*(a+c)*(b+d);
    //  if (denom==0)
    //    return 0;
    //  float Phi = (a*d-b*c)/sqrt(denom);
    //  return Phi;
    if((a+b)==0) return 0;
    if((c+d)==0) return 0;
    if((a+c)==0) return 0;
    if((b+d)==0) return 0;
    // avoid the computation of denom, possibly bigger than an int or an unsigned long long int...
    return (a*d-b*c)/(sqrt((float)(a+b))*sqrt((float)(c+d))*sqrt((float)(a+c))*sqrt((float)(b+d)));
}

/*Computes the chi2 value of the matrix 2*number_of_read_sets */
float rank_phi_N (const int *sum_up, const int *sum_lo, const int number_of_read_sets) {
    if (number_of_read_sets==1)
        return 0;
    int i;
    float n=0; for (i=0;i<number_of_read_sets;i++) n+=sum_up[i]+sum_lo[i];
    float all_up=0; for (i=0;i<number_of_read_sets;i++) all_up+=sum_up[i];
    float all_lo=0; for (i=0;i<number_of_read_sets;i++) all_lo+=sum_lo[i];
    float expected;
    
    
    float som=0;
    for(i=0;i<number_of_read_sets;i++){
        // UPPER PATH
        expected=(sum_up[i]+sum_lo[i])*all_up/n;
        if(expected!=0) som+=pow(sum_up[i]-expected,2)/expected;
        // LOWER PATH
        expected=(sum_up[i]+sum_lo[i])*all_lo/n;
        if(expected!=0) som+=pow(sum_lo[i]-expected,2)/expected;
    }
    
    return sqrt(som/n);
}

/*Computes all pairwise phi values for all pairs of conditions and returns the max*/
float rank_phi(const int *sum_up, const int *sum_lo, const int number_of_read_sets) {
    float phimax=0;
    if (number_of_read_sets==1)
        return 0;
    else
    {
        int i,j;
        float phicur=0;
        for (i=0;i<number_of_read_sets;i++)
            for (j=i+1;j<number_of_read_sets;j++)
            {
                phicur=phi(sum_up[i],sum_up[j],sum_lo[i],sum_lo[j]);
                phimax=MAX(phimax,ABS(phicur));
            }
    }
    return phimax;
}

#ifdef INPUT_FROM_KISSPLICE
/**
 * prints a couple using the reads starting position instead of coverage per position
 */
void print_couple_i(char * comment, FILE* out, const p_fragment_info * results_against_set, int cycle_id, int number_of_read_sets, int qual, const char map_snps)
{
  int read_set_id;
  int sum_up[number_of_read_sets] ;
  int sum_lo[number_of_read_sets] ;
  for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
  {
    sum_up[read_set_id]=results_against_set[cycle_id]->nb_reads_overlapping_AS[read_set_id] + results_against_set[cycle_id]->nb_reads_overlapping_SB[read_set_id] +  results_against_set[cycle_id]->nb_reads_fully_in_S[read_set_id] - results_against_set[cycle_id]->nb_reads_overlapping_both_AS_and_SB[read_set_id];
    sum_lo[read_set_id]=results_against_set[cycle_id + 1]->nb_reads_overlapping_both_AS_and_SB[read_set_id];
  }
  float rank = rank_phi_N(sum_up,sum_lo,number_of_read_sets);
  if (!standard_fasta)
  {
    // UPPER PATH
    fprintf(out, "%2f >%s%s|", rank, comment,results_against_set[cycle_id]->comment);
    if (countingOption == 0)
    {
      for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
      {
        fprintf(out,  "C%d_%d|",read_set_id+1, sum_up[read_set_id]);
      }
    }
    else if (countingOption == 1)
    { // only the junctions
      for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
      {
        fprintf(out, "AS%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_AS[read_set_id]);
        fprintf(out, "SB%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_SB[read_set_id]);
        fprintf(out, "ASSB%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_both_AS_and_SB[read_set_id]);
      }
    }
    else if (countingOption == 2)
    {//all counts
      for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
      {
        fprintf(out, "AS%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_AS[read_set_id]);
        fprintf(out, "SB%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_SB[read_set_id]);
        fprintf(out, "S%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_fully_in_S[read_set_id]);
        fprintf(out, "ASSB%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_both_AS_and_SB[read_set_id]);
      }}
    fprintf(out, "rank_%.5f",rank);
    fprintf(out, ";%s%s%s;", results_against_set[cycle_id]->left_extension, results_against_set[cycle_id]->w, results_against_set[cycle_id]->right_extension);
    // LOWER PATH
    fprintf(out, ">%s%s|", comment, results_against_set[cycle_id+1]->comment);
    char * optionsCounts = ( countingOption == 0) ? "C" : "AB" ;
    for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
    {
      fprintf(out, "%s%d_%d|",optionsCounts, read_set_id+1, sum_lo[read_set_id]);
    }
    fprintf(out, "rank_%.5f",rank);
    fprintf(out, ";%s%s%s\n", results_against_set[cycle_id+1]->left_extension, results_against_set[cycle_id+1]->w, results_against_set[cycle_id+1]->right_extension);
  }
  else // standard fasta, only one output possible
{
  // UPPER PATH
  fprintf(out, ">%s%s|", comment,results_against_set[cycle_id]->comment);
  for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
  {
    fprintf(out, "AS%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_AS[read_set_id]);
    fprintf(out, "SB%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_SB[read_set_id]);
    fprintf(out, "S%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_fully_in_S[read_set_id]);
    fprintf(out, "ASSB%d_%d|",read_set_id+1,results_against_set[cycle_id]->nb_reads_overlapping_both_AS_and_SB[read_set_id]);
  }
  fprintf(out, "rank_%.5f",rank);
  fprintf(out, "\n%s%s%s\n", results_against_set[cycle_id]->left_extension, results_against_set[cycle_id]->w, results_against_set[cycle_id]->right_extension);
  // LOWER PATH
  fprintf(out, ">%s%s|", comment, results_against_set[cycle_id+1]->comment);
  for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
    fprintf(out, "AB%d_%d|",read_set_id+1,results_against_set[cycle_id+1]->nb_reads_overlapping_both_AS_and_SB[read_set_id]);
  fprintf(out, "rank_%.5f",rank);
  fprintf(out, "\n%s%s%s\n", results_against_set[cycle_id+1]->left_extension, results_against_set[cycle_id+1]->w, results_against_set[cycle_id+1]->right_extension);
}
}
#else // INPUT_FROM_KISSPLICE

/**
 * prints a couple using the reads starting position instead of coverage per position
 */
void print_couple_i(char * comment, FILE* out, const p_fragment_info * results_against_set, int cycle_id, int number_of_read_sets, int qual, const char map_snps){
	
    // on upper path
	int sum_up[number_of_read_sets];
	int avg_up[number_of_read_sets];
    
	// on lower path
	int sum_lo[number_of_read_sets];
	int avg_lo[number_of_read_sets];
    
    
	int read_set_id;
    
	if( qual ){
        // we are providing results for generic dataset
        //        if(!map_snps){ // TODO: UNTESTED CODE.
        //            for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
        //                avg_up[read_set_id] = 0;
        //                for (j=kmer_size-1;j<=strlen(results_against_set[cycle_id]->w)-kmer_size;j++){
        //                    if(results_against_set[cycle_id]->read_coherent_positions[read_set_id][j])
        //#ifdef CHARQUAL  // FIXME: IT SHOULKD BE THE OPOSIT NO ? (PIERRE APRL 2013)
        //                        avg_up[read_set_id] = avg_up[read_set_id] + results_against_set[cycle_id]->sum_quality_per_position[read_set_id][j];
        //#else
        //                    avg_up[read_set_id] = avg_up[read_set_id] + (results_against_set[cycle_id]->sum_quality_per_position[read_set_id][j] / results_against_set[cycle_id]->read_coherent_positions[read_set_id][j]);
        //#endif
        //                }
        //            }
        //            for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
        //                avg_lo[read_set_id] = 0;
        //                for (j=kmer_size-1;j<=strlen(results_against_set[cycle_id+1]->w)-kmer_size;j++){
        //                    if(results_against_set[cycle_id+1]->read_coherent_positions[read_set_id][j])
        //#ifdef CHARQUAL  // FIXME: IT SHOULKD BE THE OPOSIT NO ? (PIERRE APRL 2013)
        //                        avg_lo[read_set_id] = avg_lo[read_set_id] + results_against_set[cycle_id+1]->sum_quality_per_position[read_set_id][j];
        //#else
        //                    avg_lo[read_set_id] = avg_lo[read_set_id] + (results_against_set[cycle_id+1]->sum_quality_per_position[read_set_id][j] / results_against_set[cycle_id+1]->read_coherent_positions[read_set_id][j]);
        //#endif
        //                }
        //            }
        //        } // END TODO.
        //        else{ // we are providing results for a SNP or a splicing..., we give outputs only for the central position
        
        //compute average quality for the variant (position quality if SNP)
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
            avg_up[read_set_id] = 0;
            const int snp_pos = strlen(results_against_set[cycle_id]->w)/2;
            if(results_against_set[cycle_id]->read_coherent_positions[read_set_id][snp_pos])
#ifdef CHARQUAL  // FIXME: IT SHOULKD BE THE OPOSIT NO ? (PIERRE APRL 2013)
                avg_up[read_set_id] = avg_up[read_set_id] + results_against_set[cycle_id]->sum_quality_per_position[read_set_id][snp_pos];
#else
            avg_up[read_set_id] = avg_up[read_set_id] + (results_against_set[cycle_id]->sum_quality_per_position[read_set_id][snp_pos] / results_against_set[cycle_id]->read_coherent_positions[read_set_id][snp_pos]);
#endif
            //              avg_up[read_set_id] = avg_up[read_set_id] / (strlen(results_against_set[cycle_id]->w) - 2*kmer_size + 2);
        }
        //compute average quality for the variant (position quality if SNP)
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
            avg_lo[read_set_id] = 0;
            const int snp_pos = strlen(results_against_set[cycle_id+1]->w)/2;
            if(results_against_set[cycle_id+1]->read_coherent_positions[read_set_id][snp_pos])
#ifdef CHARQUAL  // FIXME: IT SHOULD BE THE OPOSIT NO ? (PIERRE APRL 2013)
                avg_lo[read_set_id] = avg_lo[read_set_id] + results_against_set[cycle_id+1]->sum_quality_per_position[read_set_id][snp_pos];
#else
            avg_lo[read_set_id] = avg_lo[read_set_id] + (results_against_set[cycle_id+1]->sum_quality_per_position[read_set_id][snp_pos] / results_against_set[cycle_id+1]->read_coherent_positions[read_set_id][snp_pos]);
#endif
            //              avg_lo[read_set_id] = avg_lo[read_set_id] / (strlen(results_against_set[cycle_id+1]->w) - 2*kmer_size + 2);
        }
        //        }
	}
	
	//	float sum=0;
	for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
		/// UPPER
		sum_up[read_set_id]=results_against_set[cycle_id]->number_mapped_reads[read_set_id];
        //		compute_min_max_sum_starting_reads(results_against_set[read_set_id][cycle_id], &min_up[read_set_id], &max_up[read_set_id], &sum_up[read_set_id]);
		/// LOWER
		sum_lo[read_set_id]=results_against_set[cycle_id+1]->number_mapped_reads[read_set_id];
		//compute_min_max_sum_starting_reads(results_against_set[read_set_id][cycle_id+1], &min_lo[read_set_id], &max_lo[read_set_id], &sum_lo[read_set_id]);
	}
    
    if (!standard_fasta)
    {
        float rank = rank_phi_N(sum_up,sum_lo,number_of_read_sets);
        
        // UPPER PATH
        //fprintf(out, ">%s%s|", comment,results_against_set[cycle_id]->comment);
        fprintf(out, "%2f >%s%s|", rank, comment,results_against_set[cycle_id]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
            fprintf(out, "C%d_%d|",read_set_id+1,sum_up[read_set_id]);
        if (qual)
            for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
                fprintf(out, "Q%d_%d|",read_set_id+1,avg_up[read_set_id]);
        fprintf(out, "rank_%.5f",rank);
        //#ifdef GET_ONLY_UPPER_CHARS
        if(map_snps)
            fprintf(out, ";%s%s%s", results_against_set[cycle_id]->left_extension, results_against_set[cycle_id]->w, results_against_set[cycle_id]->right_extension);
        //#else
        else
            fprintf(out, ";%s", results_against_set[cycle_id]->w);
        //#endif
        fprintf(out, ";");
        
        // LOWER PATH
        fprintf(out, ">%s%s|", comment, results_against_set[cycle_id+1]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
            fprintf(out, "C%d_%d|",read_set_id+1,sum_lo[read_set_id]);
        if ( qual )
            for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
                fprintf(out, "Q%d_%d|",read_set_id+1,avg_lo[read_set_id]);
        fprintf(out, "rank_%.5f",rank);
        //#ifdef GET_ONLY_UPPER_CHARS
        if(map_snps)
            fprintf(out, ";%s%s%s", results_against_set[cycle_id+1]->left_extension, results_against_set[cycle_id+1]->w, results_against_set[cycle_id+1]->right_extension);
        //#else
        else
            fprintf(out, ";%s", results_against_set[cycle_id+1]->w);
        //#endif
        
        fprintf(out, "\n");
    }
    else
    {
        // UPPER PATH
        fprintf(out, ">%s%s|", comment,results_against_set[cycle_id]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
            fprintf(out, "C%d_%d|",read_set_id+1,sum_up[read_set_id]);
        if (qual)
            for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
                fprintf(out, "Q%d_%d|",read_set_id+1,avg_up[read_set_id]);
        //#ifdef GET_ONLY_UPPER_CHARS
        if(map_snps)
            fprintf(out, ";%s%s%s", results_against_set[cycle_id]->left_extension, results_against_set[cycle_id]->w, results_against_set[cycle_id]->right_extension);
        //#else
        else
            fprintf(out, ";%s", results_against_set[cycle_id]->w);
        //#endif
        
        
        // LOWER PATH
        fprintf(out, ">%s%s|", comment, results_against_set[cycle_id+1]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
            fprintf(out, "C%d_%d|",read_set_id+1,sum_lo[read_set_id]);
        if ( qual )
            for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++)
                fprintf(out, "Q%d_%d|",read_set_id+1,avg_lo[read_set_id]);
        //#ifdef GET_ONLY_UPPER_CHARS
        if(map_snps)
            fprintf(out, ";%s%s%s", results_against_set[cycle_id+1]->left_extension, results_against_set[cycle_id+1]->w, results_against_set[cycle_id+1]->right_extension);
        //#else
        else
            fprintf(out, ";%s", results_against_set[cycle_id+1]->w);
        //#endif
    }
    
	
}


#endif // INPUT_FROM_KISSPLICE


/**
 * prints a couple using the reads starting position instead of coverage per position
 */
void print_quadruplet_i(FILE* out, const p_fragment_info * results_against_set, int cycle_id, int number_of_read_sets, int qual){
    int j;
	int cov_1[number_of_read_sets] ; // coverage path 1
    int cov_2[number_of_read_sets] ; // coverage path 2
    int cov_3[number_of_read_sets] ; // coverage path 3
    int cov_4[number_of_read_sets] ; // coverage path 4
    
    
    int qual_1[number_of_read_sets]; // quality path 1
    int qual_2[number_of_read_sets]; // quality path 2
    int qual_3[number_of_read_sets]; // quality path 3
    int qual_4[number_of_read_sets]; // quality path 4
    int read_set_id;
    
	if( qual ){// TODO: UNTESTED CODE - APRIL 2013
        // we are providing results for generic dataset
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
            qual_1[read_set_id] = 0;
            qual_2[read_set_id] = 0;
            qual_3[read_set_id] = 0;
            qual_4[read_set_id] = 0;
            for (j=kmer_size-1;j<=strlen(results_against_set[cycle_id]->w)-kmer_size;j++){
#ifdef CHARQUAL // FIXME: IT SHOULKD BE THE OPOSIT NO ? (PIERRE APRL 2013)
                if(results_against_set[cycle_id]->read_coherent_positions[read_set_id][j]) qual_1[read_set_id] = qual_1[read_set_id] + results_against_set[cycle_id]->sum_quality_per_position[read_set_id][j];
                if(results_against_set[cycle_id+1]->read_coherent_positions[read_set_id][j]) qual_2[read_set_id] = qual_2[read_set_id] + results_against_set[cycle_id+1]->sum_quality_per_position[read_set_id][j];
                if(results_against_set[cycle_id+2]->read_coherent_positions[read_set_id][j]) qual_3[read_set_id] = qual_3[read_set_id] + results_against_set[cycle_id+2]->sum_quality_per_position[read_set_id][j];
                if(results_against_set[cycle_id+3]->read_coherent_positions[read_set_id][j]) qual_4[read_set_id] = qual_4[read_set_id] + results_against_set[cycle_id+3]->sum_quality_per_position[read_set_id][j];
#else
                if(results_against_set[cycle_id]->read_coherent_positions[read_set_id][j]) qual_1[read_set_id] = qual_1[read_set_id] + (results_against_set[cycle_id]->sum_quality_per_position[read_set_id][j] / results_against_set[cycle_id]->read_coherent_positions[read_set_id][j]);
                if(results_against_set[cycle_id+1]->read_coherent_positions[read_set_id][j]) qual_2[read_set_id] = qual_2[read_set_id] + (results_against_set[cycle_id+1]->sum_quality_per_position[read_set_id][j] / results_against_set[cycle_id+1]->read_coherent_positions[read_set_id][j]);
                if(results_against_set[cycle_id+2]->read_coherent_positions[read_set_id][j]) qual_3[read_set_id] = qual_3[read_set_id] + (results_against_set[cycle_id+2]->sum_quality_per_position[read_set_id][j] / results_against_set[cycle_id+2]->read_coherent_positions[read_set_id][j]);
                if(results_against_set[cycle_id+3]->read_coherent_positions[read_set_id][j]) qual_4[read_set_id] = qual_4[read_set_id] + (results_against_set[cycle_id+3]->sum_quality_per_position[read_set_id][j] / results_against_set[cycle_id+3]->read_coherent_positions[read_set_id][j]);
                
#endif
            }
        }
    } // END UNTESTED CODE
	
	//	float sum=0;
	for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++){
		cov_1[read_set_id]=results_against_set[cycle_id]->number_mapped_reads[read_set_id];
        cov_2[read_set_id]=results_against_set[cycle_id+1]->number_mapped_reads[read_set_id];
        cov_3[read_set_id]=results_against_set[cycle_id+2]->number_mapped_reads[read_set_id];
        cov_4[read_set_id]=results_against_set[cycle_id+3]->number_mapped_reads[read_set_id];
	}
    //  float rank = rank_phi(sum_up,sum_lo,number_of_read_sets);
    float rank=0;
    
    if (!standard_fasta)
    {
        // PATH1
        fprintf(out, "%2f >%s|", rank, results_against_set[cycle_id]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_1[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_1[read_set_id]);
        fprintf(out, "rank_%.5f",rank);
        fprintf(out, ";%s", results_against_set[cycle_id]->w);
        fprintf(out, ";");
        
        // PATH2
        fprintf(out, "%2f >%s|", rank, results_against_set[cycle_id+1]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_2[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_2[read_set_id]);
        fprintf(out, "rank_%.5f",rank);
        fprintf(out, ";%s", results_against_set[cycle_id+1]->w);
        fprintf(out, ";");
        
        // PATH3
        fprintf(out, "%2f >%s|", rank, results_against_set[cycle_id+2]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_3[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_3[read_set_id]);
        fprintf(out, "rank_%.5f",rank);
        fprintf(out, ";%s", results_against_set[cycle_id+2]->w);
        fprintf(out, ";");
        
        // PATH4
        fprintf(out, "%2f >%s|", rank, results_against_set[cycle_id+3]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_4[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_4[read_set_id]);
        fprintf(out, "rank_%.5f",rank);
        fprintf(out, ";%s", results_against_set[cycle_id+3]->w);
        fprintf(out, ";");
        
        fprintf(out, "\n");
    }
    else
    {
        // PATH1
        fprintf(out, ">%s|", results_against_set[cycle_id]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_1[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_1[read_set_id]);
        fprintf(out, "rank_%.5f\n",rank);
        fprintf(out, "%s\n", results_against_set[cycle_id]->w);
        
        // PATH2
        fprintf(out, ">%s|", results_against_set[cycle_id+1]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_2[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_2[read_set_id]);
        fprintf(out, "rank_%.5f\n",rank);
        fprintf(out, "%s\n", results_against_set[cycle_id+1]->w);
        
        // PATH3
        fprintf(out, ">%s|", results_against_set[cycle_id+2]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_3[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_3[read_set_id]);
        fprintf(out, "rank_%.5f\n",rank);
        fprintf(out, "%s\n", results_against_set[cycle_id+2]->w);
        
        // PATH4
        fprintf(out, ">%s|", results_against_set[cycle_id+3]->comment);
        for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "C%d_%d|",read_set_id+1,cov_4[read_set_id]);
        if (qual) for(read_set_id=0;read_set_id<number_of_read_sets;read_set_id++) fprintf(out, "Q%d_%d|",read_set_id+1,qual_4[read_set_id]);
        fprintf(out, "rank_%.5f\n",rank);
        fprintf(out, "%s\n", results_against_set[cycle_id+3]->w);
    }
    
	
}

/**
 * checks if at least one read set provide read coherency for a path.
 */
inline int one_coherent(const p_fragment_info * results_against_set, int cycle_id, int number_of_read_sets){
	int i;
	for(i=0;i<number_of_read_sets;i++){
        if(results_against_set[cycle_id]->read_coherent[i]) return 1;
		
	}
	return 0;
}


void print_results_2_paths_per_event(FILE * coherent_out, FILE * uncoherent_out,  const p_fragment_info * results_against_set, const int number_of_read_sets, int nb_events_per_set, int qual){
    int i;
	int nb_read_coherent=0;
	int nb_unread_coherent=0;
	//printf("number ofread sets = %d\n", number_of_read_sets);
    
    //
    //                 C1           C2           C3 ....
    // path1 (i)      [0/1]        [0/1]        [0/1]...
    // path2 (i+1)    [0/1]        [0/1]        [0/1]...
    //
    // event is kept only if each line has at least one "1" per line:
    //
    
	
    
	for(i=0;i<nb_events_per_set*2;i+=2){
		if(one_coherent(results_against_set,i,number_of_read_sets) && one_coherent(results_against_set,i+1,number_of_read_sets))
		{
			nb_read_coherent++;
			print_couple_i("",coherent_out, results_against_set, i, number_of_read_sets, qual, 1);
		}
		else{
			nb_unread_coherent++;
			print_couple_i("", uncoherent_out, results_against_set, i, number_of_read_sets, qual, 1);
		}
	}
    
	printf("Among %d bubbles:\n\t%d read coherent and\n\t%d not read coherent\n",
           nb_events_per_set, nb_read_coherent, nb_unread_coherent);
}

//#define LIVIUS_TESTS

#ifdef LIVIUS_TESTS

void print_results_invs(FILE * coherent_out, FILE * uncoherent_out,  const p_fragment_info * results_against_set, const int number_of_read_sets, int nb_events_per_set, int qual){
    int i;
	int nb_read_coherent=0;
	int nb_unread_coherent=0;
    //                     C1           C2
    // au  path1 (i)      [0/1]        [0/1]
    // vb  path2 (i+1)    [0/1]        [0/1]
    // av' path2 (i+2)    [0/1]        [0/1]
    // u'b path2 (i+3)    [0/1]        [0/1]
    if(number_of_read_sets!=2){
        fprintf(stderr,"this kind of test is available only on exactly 2 datasets - please use 2 datasets or recompile kissreads after commenting ligne \"#define LIVIUS_TESTS\"\n");
        exit(1);
    }
    printf("OUTPUTS ONLY MOTIFS WHERE au-vb is specific to one datasets and av'-u'b is specific to the other\n");
    
    for(i=0;i<nb_events_per_set*4;i+=4){
        char coherent=0;
        if(results_against_set[i]->read_coherent[0] && results_against_set[i+1]->read_coherent[0] && //au and vb coherent in C1
           (!results_against_set[i+2]->read_coherent[0] || !results_against_set[i+3]->read_coherent[0]) && //av' or u'b uncoherent in C1
           (!results_against_set[i]->read_coherent[1] || !results_against_set[i+1]->read_coherent[1]) && //au or vb uncoherent in C2
           results_against_set[i+2]->read_coherent[1] && results_against_set[i+3]->read_coherent[1]) //av' and u'b coherent in C2
            coherent = 1;
        if(results_against_set[i]->read_coherent[1] && results_against_set[i+1]->read_coherent[1] && //au and vb coherent in C2
           (!results_against_set[i+2]->read_coherent[1] || !results_against_set[i+3]->read_coherent[1]) && //av' or u'b uncoherent in C2
           (!results_against_set[i]->read_coherent[0] || !results_against_set[i+1]->read_coherent[0]) && //au or vb uncoherent in C1
           results_against_set[i+2]->read_coherent[0] && results_against_set[i+3]->read_coherent[0]) //av' and u'b coherent in C1
            coherent=1;
        if(coherent){
			nb_read_coherent++;
			print_quadruplet_i(coherent_out, results_against_set, i, number_of_read_sets, qual);
		}
		else{
			nb_unread_coherent++;
			print_quadruplet_i(uncoherent_out, results_against_set, i, number_of_read_sets, qual);
		}
	}
    
	printf("Among %d bubbles:\n\t%d read coherent and\n\t%d not read coherent\n",
           nb_events_per_set, nb_read_coherent, nb_unread_coherent);
    
    
}
#else // LIVIUS_TESTS

void print_results_invs(FILE * coherent_out, FILE * uncoherent_out,  const p_fragment_info * results_against_set, const int number_of_read_sets, int nb_events_per_set, int qual){
    int i;
	int nb_read_coherent=0;
	int nb_unread_coherent=0;
	//printf("number ofread sets = %d\n", number_of_read_sets);
    
    //
    //                 C1           C2           C3 ....
    // path1 (i)      [0/1]        [0/1]        [0/1]...
    // path2 (i+1)    [0/1]        [0/1]        [0/1]...
    // path2 (i+2)    [0/1]        [0/1]        [0/1]...
    // path2 (i+3)    [0/1]        [0/1]        [0/1]...
    //
    // event is kept only if each line has at least one "1" per line:
    //
    
	
    
	for(i=0;i<nb_events_per_set*4;i+=4){
		if(one_coherent(results_against_set,i,number_of_read_sets) &&
           one_coherent(results_against_set,i+1,number_of_read_sets) &&
           one_coherent(results_against_set,i+2,number_of_read_sets) &&
           one_coherent(results_against_set,i+3,number_of_read_sets)
           )
		{
			nb_read_coherent++;
			print_quadruplet_i(coherent_out, results_against_set, i, number_of_read_sets, qual);
		}
		else{
			nb_unread_coherent++;
			print_quadruplet_i(uncoherent_out, results_against_set, i, number_of_read_sets, qual);
		}
	}
    
	printf("Among %d bubbles:\n\t%d read coherent and\n\t%d not read coherent\n",
           nb_events_per_set, nb_read_coherent, nb_unread_coherent);
}
#endif // LIVIUS_TESTS










