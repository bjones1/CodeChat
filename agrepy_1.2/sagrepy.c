/* This file corresponds as closely as possible to the file sgrep.c, from
   agrep 2.04, to the extent that it implements string search with indels.
   In the orginal implementation, function agrep is used for simple patterns
   i.e. not involving regular expressions, which are less that length 24.
   Before agrep is called, prep and initmask are used to set up some global
   data areas.

   The assumption is that r.e. matching will be done by the re or regexp modules
   and that straight string matching will be done be find/rfind in the string
   module, so these aspects are of no interest here. Errors in regular expressions
   will also be ignored*/

#include "agrepy.h"
/*
#define DEBUGDEBUG
*/

int INT_BYTES = sizeof(int);



/* The  number of errors is the lowest numbered member of R with a zero in
   it, excluding i leading zeros, where i is the index of R. If there is still a leading
   zero and the rest 1's, then a match has just happened on this letter */

int count_errors(register unsigned int *R, int D, register unsigned int Bit1)
{
  register unsigned int i, j, top_bits, new_start;

  new_start = -1;

  top_bits = Bit1;
  for(i=0; i<=D; i++)
    {
    /* Now check if R[i] contains a zero, excluding all leading zeros */
    j = ~R[i] << i;
    while (j & Bit1)  /* ie MSB is set */
      j <<= 1;
    if(j > 0)
      return(i);

    /*	If it gets to here, j == 0, i.e. all 1's after initial zeros
	so if new_start is not already set test for MSB after lead bits 0. If it 0 potential
	starting point */
    if(new_start == -1 && (R[i] & top_bits) == 0)
        new_start = i;
    top_bits = (top_bits >> 1) | Bit1;
    }

  /* there are no embedded zeros, e.g. during initial match */
  return(new_start);
}

/* return the position of the highest numbered 0, with MSB numbered 0 */
  
int furthest_zero(unsigned int bits)
{
  register int pos;
  register unsigned int b = bits;

  pos = 2 * INT_BYTES - 1;
  for( ; pos >= 0; pos--)
    {
    switch (b & 0xF) 
      {
      case 0x0 :
      case 0x2 :
      case 0x4 :
      case 0x6 :
      case 0x8 :
      case 0xA :
      case 0xC :
      case 0xE : return(4 * pos + 3);
      case 0x1 :
      case 0x5 :
      case 0x9 :
      case 0xD : return(4 * pos + 2);
      case 0x3 :
      case 0xB : return(4 * pos + 1);
      case 0x7 : return(4 * pos);
      case 0xF : /* Try next byte */ ;
      }
    b >>= 4;
    }
 
  return(-1);

}

/* Given a pattern string and a text string, and knowing that there is
   a match between the two containing at most max_errs errors
   return the initial matching position and, in case the ends of
   the two strings do not represent a match, the final text match position.
   if two solutions differ in the number of errors, choose the lesser;
   if they have equal errors, choose the one whose first match is closer to the start of
   the pattern;
   finally, if they have equal error and equal starting position, choose the one that
   has the smaller end position (ie. more compact match from pov of text) */

int find_start_pos_main(char *patn, int patend, char *text, int textend, int *lastpatok, int lastok,
		int max_errs, int *nerrors, int *firstok, int *firstpatok)
{
  int i, j, k, l, newlastok, newerrs, newfirstok, newfirstpatok;

#ifdef DEBUGDEBUG
  printf("patend %c/%d textend %c/%d lastok %d, lastpatok %d, *nerrors %d\n", patn[patend], patend, text[textend], textend, lastok, *lastpatok, *nerrors);
#endif

  if(patend == -1 || *nerrors > max_errs)
    return(lastok);

  if(patn[patend] == text[textend])
    {
    if(textend > *firstok)  /* covers any slopiness in defining endpoint */
	{
	*firstok = textend;
	*firstpatok = patend;
	*nerrors = strlen(patn) - patend - 1;
#ifdef DEBUGDEBUG
  printf("New highest point in text found %d, error reset to %d, firstpatok %d\n", textend, *nerrors, *firstpatok);
#endif
	}
    if(patend < *lastpatok)
	{
	*lastpatok = patend;
	}

    return(find_start_pos_main(patn, patend-1, text, textend-1, lastpatok,
						textend, max_errs, nerrors, firstok, firstpatok));
    }

  /* mismatch so find best place upstream to resume matching */

  newerrs = *nerrors + 1;
  newfirstok = *firstok;
  newfirstpatok = *firstpatok;
  newlastok = find_start_pos_main(patn, patend, text, textend-1,
						lastpatok, lastok, max_errs, &newerrs, &newfirstok, &newfirstpatok);

  j = *nerrors + 1;
  k = *firstok;
  l = *firstpatok;
  i = find_start_pos_main(patn, patend-1, text, textend-1, lastpatok, lastok,
								max_errs, &j, &k, &l);
  if(j < newerrs || ((j == newerrs) &&  (i < newlastok)) || ((j == newerrs) && (i == newlastok) && (k < newfirstok)))
    {
    newerrs = j; 
    newlastok = i;
    newfirstok = k;
    newfirstpatok = l;
    }

  j = *nerrors + 1;
  k = *firstok;
  l = *firstpatok;
  i = find_start_pos_main(patn, patend-1, text, textend, lastpatok, lastok,
								max_errs, &j, &k, &l);
  if(j < newerrs || ((j == newerrs) &&  (i < newlastok)) || ((j == newerrs) && (i == newlastok) && (k < newfirstok)))
    {
    newerrs = j; 
    newlastok = i;
    newfirstok = k;
    newfirstpatok = l;
    }

  *nerrors = newerrs;
  *firstok = newfirstok;
  *firstpatok = newfirstpatok;
  return(newlastok);
}

int find_start_pos(char *patn, int patend, char *text, int textend, int max_errs,
		int *firstok, boolean gotoends)
{
  int nerrors = 0, lastpatok = patend, firstpatok = -1, textstart;

  *firstok = -1;
  textstart = find_start_pos_main(patn, patend, text, textend, &lastpatok, textend,
				max_errs, &nerrors, firstok, &firstpatok);
  if(! gotoends)  /* Assume extent is from first character match to last */
    return(textstart);

  textstart -= lastpatok; /* Else account for distance to start of pattern */
  *firstok += (strlen(patn) - firstpatok - 1);  /* and distance from last match to end of pattern */
  return(textstart);
}



int_pair_list *exec_sagrepy(char *pat, int M, char *text, int text_len, boolean gotoends,
		param_struct *parampt)
{
  register signed char D = parampt -> sagrep.NErrors;
  register int i;
  register int m = M/(D+1);
  register char  *textstart;
  register int shift, HASH;
  int  j=0, k, m1, d1;
  int  n, cdx;
  int  Candidate[2048 ][2], round;
  unsigned int R1[20 +1], R2[20 +1]; 
  register unsigned int r1, endpos, c; 
  unsigned int currentpos;
  unsigned int Bit1;
  int match_start = -1, /* start of a match  */
      match_end = -1,
      NErrors = -1,	/* Actual number of errors <= D  */
      furthest = -1,	/* furthest point down a pattern achieved with D errors */
      wind_fwd = -1;	/* Match will stop short if actual number of errors < D, so
			   this will be used to wind the match forward to last real matching char */
  char *textend = text + text_len;
  int_pair_list *matches = NULL;


  Candidate[0][0] = Candidate[0][1] = 0; 
  d1 = parampt -> sagrep.shift_1;
  cdx = 0;
  if(m < 3) r1 = m;
  else r1 = 3;
  textstart = text;
  shift = m-1;
  while (text < textend)
    {
    shift = parampt -> sagrep.SHIFT[*(text += shift)];
    while(shift)
      shift = parampt -> sagrep.SHIFT[*(text += shift)];
    HASH = *text;
    for(j = 1; j < r1; j++)
      HASH = (HASH << 2) + *(text-j);
    if (parampt -> sagrep.MEMBER[HASH])
      { 
      i = text - textstart;
      if((i - M - D - 10) > Candidate[cdx][1])
	{ 	
	Candidate[++cdx][0] = i-M-D-2;
	Candidate[cdx][1] = i+M+D;
	}
      else
	Candidate[cdx][1] = i+M+D;
      shift = d1;
      }
    else
      shift = d1;
    }

  text = textstart;
  n = textend - textstart;
  /* for those candidate areas, find the D-error matches                     */
  if(Candidate[1][0] < 0)
    Candidate[1][0] = 0;
  endpos = parampt -> sagrep.endposition;                /* the mask table and the endposition */
  Bit1 = (1 << 31);
  for(round = 0; round <= cdx; round++)
    {
    i = Candidate[round][0] ; 
    if(Candidate[round][1] > n)
      Candidate[round][1] = n;
    if(i < 0)
      i = 0;

    R1[0] = R2[0] = ~0;
    R1[1] = R2[1] = ~Bit1;
    for(k = 1; k <= D; k++)
      R1[k] = R2[k] = (R1[k-1] >> 1) & R1[k-1];
    while (i < Candidate[round][1])                     
      {
      c = text[i++];
      r1 = parampt -> sagrep.Mask[c];
      R1[0] = (R2[0] >> 1) | r1;
#ifdef DEBUGDEBUG
      printf("Text[%d]:%c R1[0]:%d", i-1, c, furthest_zero(R1[0]));
#endif
      for(k=1; k<=D; k++)
	{
	R1[k] = ((R2[k] >> 1) | r1) & R2[k-1] & ((R1[k-1] & R2[k-1]) >> 1);
#ifdef DEBUGDEBUG
	printf(" R1[%d]:%d", k, furthest_zero(R1[k]));
#endif
	}
#ifdef DEBUGDEBUG
      NErrors = count_errors(R1, D, Bit1);
      printf("  End: %d NErrors: %d\n", (R1[D] & endpos) > 0, NErrors);
#endif
      if((R1[D] & endpos) == 0)
	{ 
	NErrors = count_errors(R1, D, Bit1);
	if((k = furthest_zero(R1[D])) > furthest)
	  furthest = k;
	NErrors = D - NErrors;
	match_start = find_start_pos(pat, furthest, text, i-1+NErrors, D, &match_end, gotoends);
#ifdef DEBUG
	printf("Match1 from %d to %d ",match_start, match_end);
	printnstring(text, match_start, match_end);
	putc('\n', stdout);
#endif
	matches = add_ends(match_start, match_end, matches);
	currentpos = i;
	for(k=0; k<=D; k++)
	    R1[k] = R2[k] = ~0;
	}
      c = text[i++];
      r1 = parampt -> sagrep.Mask[c];
      R2[0] = (R1[0] >> 1) | r1;
#ifdef DEBUGDEBUG
      printf("Text[%d]:%c R2[0]:%d", i-1, c, furthest_zero(R2[0]));
#endif
      for(k = 1; k <= D; k++)
	{
	R2[k] = ((R1[k] >> 1) | r1) & R1[k-1] & ((R1[k-1] & R2[k-1]) >> 1);
#ifdef DEBUGDEBUG
	printf(" R2[%d]:%d", k, furthest_zero(R2[k]));
#endif
	}
#ifdef DEBUGDEBUG
      NErrors = count_errors(R2, D, Bit1);
      printf("  End: %d  NErrors: %d\n", (R2[D] & endpos) > 0, NErrors);
#endif
      if((R2[D] & endpos) == 0 || wind_fwd >= 0)
	{ 
	NErrors = count_errors(R2, D, Bit1);
	if((k = furthest_zero(R2[D])) > furthest)
	  furthest = k;

	NErrors = D - NErrors;
	match_start = find_start_pos(pat, furthest, text, i-1+NErrors, D, &match_end, gotoends);
#ifdef DEBUG
	printf("Match2 from %d to %d ",match_start,match_end);
	printnstring(text, match_start, match_end);
	putc('\n', stdout);
#endif
	matches = add_ends(match_start, match_end, matches);
	currentpos = i;
	for(k=0; k<=D; k++)
	    R1[k] = R2[k] = ~0;
	}
     }
  }
  if(matches == NULL)
    return(NULL);
  matches -> pairs = (int_pair *) realloc(matches -> pairs, (matches -> npairs + 1) * sizeof(int_pair));
  return(matches);
}

/* initmask() initializes the mask table for the pattern                    */ 
/* endposition is a mask for the endposition of the pattern                 */
/* endposition will contain k mask bits if the pattern contains k fragments */
static
void initmask(char *pattern, register int m, register int D,
			param_struct *parampt)
{
  register unsigned int Bit1, c;
  register int i, j, frag_num;

  Bit1 = 1 << 31;    /* the first bit of Bit1 is 1, others 0.  */
  frag_num = D+1;
  parampt -> sagrep.endposition = 0;
  for (i = 0; i < frag_num; i++)
    parampt -> sagrep.endposition |= (Bit1 >> i);
  parampt -> sagrep.endposition >>= (m - frag_num);
  for(i = 0; i < MAXSYM ; i++)
    parampt -> sagrep.Mask[i] = ~0;
  for(i = 0; i < m; i++)     /* initialize the mask table */
    {
    c = pattern[i];
    for ( j = 0; j < m; j++)
      if( c == pattern[j] )
	parampt -> sagrep.Mask[c] &=  ~( Bit1 >> j ) ;
    }
}

static
void prep(char *Pattern, register int M, register signed char D, param_struct *parampt)
                                  /* preprocessing for partitioning_bm */
				/* can be fine-tuned to choose a better partition */
{
  register int i, j, k, p, shift;
  register unsigned int m;
  unsigned int hash, b_size = 3;

  parampt -> sagrep.NErrors = D;
  m = M/(D+1);
  p = M - m*(D+1);
  for (i = 1; i < MAXSYM ; i++)
    parampt -> sagrep.SHIFT[i] = m;
  parampt -> sagrep.SHIFT[0] = 0;
  for (i = M-1; i>=p ; i--)
    {
    shift = (M-1-i)%m;
    hash = Pattern[i];
    if(parampt -> sagrep.SHIFT[hash] > shift)
      parampt -> sagrep.SHIFT[hash] = shift;
    }

  parampt -> sagrep.shift_1 = m;
  for(i=0; i<D+1; i++)
    {
    j = M-1 - m*i;
    for(k=1; k<m; k++)
      {
      for(p=0; p<D+1; p++) 
	if(Pattern[j-k] == Pattern[M-1-m*p]) 
      if(k < parampt -> sagrep.shift_1)
	parampt -> sagrep.shift_1 = k;
      }
    }

  if(parampt -> sagrep.shift_1 == 0)
    parampt -> sagrep.shift_1 = 1;
  for(i=0; i< MEMBER_TABLE_SIZE ; i++)
    parampt -> sagrep.MEMBER[i] = 0;
  if (m < 3)
    b_size = m;
  for(i=0; i<=D; i++)
    {
    j = M-1 - m*i;
    hash = 0;
    for(k=0; k<b_size; k++)
      hash = (hash << 2) + Pattern[j-k];
    parampt -> sagrep.MEMBER[hash] = 1;
    }
}


param_struct *sagrepy_compile(char* Pattern, int patlen, signed char NErrors)
{
    param_struct *parampt = (param_struct *) malloc(sizeof(param_struct));

    prep(Pattern, patlen, NErrors, parampt);
    initmask(Pattern, patlen, 0, parampt);
    return(parampt);
}
