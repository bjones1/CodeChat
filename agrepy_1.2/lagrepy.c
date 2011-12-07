/* lagrep is agrep for simple, i.e. non-RE patterns longer than
   24 characters, with allowed number of errors 1..8

   lagrep is a minor reworking of a_monkey; the renaming was done because
   it's more easily remembered  */

#include "agrepy.h"

/* given some text probably containing a match, verify finds the exact position
   of the match in the text and adds it to the list of matches. The value returned
   by verify is the (address of) the next place where lagrep should  continue
   the (cheaper) hash-scan. This will be one character after a verified match,
   or at the end of the allocated patch */

#define min(a, b) ((a) <= (b) ? (a) : (b))

static
char * verify(register int m, register int n, register int D, char *pat, char *text,
				char *textbegin, boolean gotoends, int_pair_list **matches)
{   
  int A[MAXPATLEN ], B[MAXPATLEN ];
  register int last = D; 
  register int d;   /* actual number of errors <= D */
  register int cost = 0;  
  register int k, i;
  register int m1 = m+1;
  char  *textend = text+n;
  char  *textrestart = text+m;  /* If nothing found, return this restart position */
  int matchend;
  char *first_text_pos = NULL;

#ifdef DEBUGDEBUG
printf("Verifying text positions %d to %d\n", text - textbegin, textend - textbegin);
#endif

  for (i = 0; i <= m1; i++) 
    A[i] = B[i] = i;

  while (text < textend && *text != '\0')
    {
    d = D;
    for (k = 1; k <= last; k++)
      {
      cost = B[k-1]+1; 
      if (pat[k-1] != *text)
	{
	if (B[k]+1 < cost)
	  cost = B[k]+1; 
	if (A[k-1]+1 < cost)
	  cost = A[k-1]+1;
	}
      else
	{
	cost = cost -1; 
	if(last == D)
	  {
#ifdef DEBUG
	  printf("Possible text start pos: %d (%c)\n", text - textbegin, *text); 
#endif
	  first_text_pos = text;
	  }
	}
      A[k] = cost; 
      if(A[k] < d && A[k] < k) /* d is min acrosss A when not in place */
	d = A[k];
      }
#ifdef DEBUG
    printf("Looking at Text[%d] %c and Patn[%d] %c, NErrors %d\n", text - textbegin, *text, last, pat[last], d);
#endif
    if(pat[last] == *text++)
      {
      if(last == D)
	{
#ifdef DEBUG
	printf("Possible text start pos: %d (%c)\n", text - textbegin - 1, *(text-1)); 
#endif
	first_text_pos = text-1;
	}
      A[last+1] = B[last];
      last++;
      }
    if(A[last] < D)
      A[last+1] = A[last++]+1;
    if (A[last] > D)
      {
	i = last;
	while (A[last] > D)
	  last = last - 1;

#ifdef DEBUG
	  printf("Winding back %d to %d/%c.\n", i - last, last, pat[last] );
#endif

	if(i - last > D)
	  {
#ifdef DEBUG
	  printf("Restart matching at text[%d]:%c\n", text - last + D -textbegin, *(text -last + D));
#endif
	  first_text_pos = text -last + D;
	  }
      }
    if(last >= m)
      {
      k = find_start_pos(pat, last - 1, textbegin, text - textbegin + D - d - 1, D, &matchend, gotoends);
      *matches = add_ends(k , matchend, *matches);
      return(textbegin + matchend + 1);
      }

    if(*text == '\0')
      break;

    d = D;
    for (k = 1; k <= last; k++)
      {
      cost = A[k-1]+1; 
      if (pat[k-1] != *text)
	{
	if (A[k]+1 < cost)
	  cost = A[k]+1; 
	if (B[k-1]+1 < cost)
	  cost = B[k-1]+1;
	}
      else 
	{
	cost = cost -1; 
	if(last == D)
	  {
#ifdef DEBUG
	  printf("Possible text start pos: %d (%c)\n", text - textbegin, *text);
#endif
	  first_text_pos = text;
	  }
	}
      B[k] = cost;
      if(B[k] < d && B[k] < k) /* less than place as well! */
	d = B[k];
      }
#ifdef DEBUG
    printf("Looking at Text[%d] %c and Patn[%d] %c, NErrors %d\n", text - textbegin, *text, last, pat[last], d);
#endif
    if(pat[last] == *text++)
      {
      if(last == D)
	{
#ifdef DEBUG
	printf("Possible text start pos: %d (%c)\n", text - textbegin - 1, *(text-1)); 
#endif
	first_text_pos = text -1;
	}
      B[last+1] = A[last];
      last++;
      }
    if(B[last] < D)
      B[last+1] = B[last++]+1;
    if (B[last] > D)
      {
	i = last;
	while (B[last] > D)
	  last = last - 1;

#ifdef DEBUG
	  printf("Winding back %d to %d/%c.\n", i - last, last, pat[last] );
#endif

	if(i - last > D)
	  {
#ifdef DEBUG
	  printf("Restart matching at text[%d]:%c\n", text - last + D -textbegin, *(text -last + D));
#endif
	  first_text_pos = text - last + D ;
	  }
      }
    if(last >= m)
      {
      k = find_start_pos(pat, last - 1, textbegin, text - textbegin + D - d - 1, D, &matchend, gotoends);
      *matches = add_ends(k , matchend, *matches);
      return(textbegin + matchend + 1);
      }
    }
  return(textrestart);
}

int_pair_list *exec_lagrepy(register char *pat, int m, register char *text, int textlen,
		boolean gotoends, param_struct *parampt) 
{
  register signed char D = parampt -> lagrep.NErrors;
  register char  *oldtext;
  register unsigned int hash, i, hashmask, suffix_error; 
  register int  m1 = m-1-D, j, pos; 
  char *textend = text + textlen, *textbegin = text;
  int_pair_list *matches = NULL;

  hashmask = parampt -> lagrep.Hashmask;
  oldtext  = text;
  while (text < textend)
    {
    text = text+m1;
    suffix_error = 0;
    while(suffix_error <= D)
      {
      hash = *text--;
      while(parampt -> lagrep.MEMBER_1[hash])
	hash = ((hash << 8 ) + *(text--)) & hashmask;
      suffix_error++;
      }
    if(text <= oldtext)
      text = verify(m, 2*m+D, D, pat, oldtext,textbegin, gotoends, &matches);
    oldtext = text; 
    }
  if(matches != NULL)
    matches -> pairs = (int_pair *) realloc(matches -> pairs, (matches -> npairs + 1) * sizeof(int_pair)); 
  return(matches);
}


static
void am_preprocess(char *Pattern, int patlen, signed char NErrors, register param_struct *parampt)
{
  register int i, j;
  unsigned int hash;

  parampt -> lagrep.NErrors = NErrors;
  for (i = 1, parampt -> lagrep.Hashmask = 1 ; i<TWOBYTES ; i++)
    parampt -> lagrep.Hashmask = (parampt -> lagrep.Hashmask << 1) + 1 ;
  for (i = 0; i < HASHTABLESIZE ; i++)
    parampt -> lagrep.MEMBER_1[i] = 0;
  for (i = patlen-1; i>=0; i--)
    parampt -> lagrep.MEMBER_1[Pattern[i]] = 1;
  for (i = patlen-1; i > 0; i--)
    parampt -> lagrep.MEMBER_1[(Pattern[i] << 8 ) + Pattern[i-1]] = 1;
}


param_struct *lagrepy_compile(char* Pattern, int patlen, signed char NErrors)
{
    param_struct *parampt = (param_struct *) malloc(sizeof(param_struct));

    am_preprocess(Pattern, patlen, NErrors, parampt);
    return(parampt);
}

