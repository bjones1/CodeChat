/* This application corresponds as closely as possible the funtionality of
   agrep 2.04, to the extent that it implements string search with indels.
   In the orginal implementation, function agrep (here called sagrep) is used
   for simple patterns i.e. not involving regular expressions, which are less
   that length SHORT_LONG (typically 24). Simple patterns longer that SHORT_LONG
   are handled by lagrep, while is known as a_monkey in the original code.

   The assumption is that r.e. matching will be done by the re or regexp modules
   and that straight string matching will be done be find/rfind in the string
   module, so these aspects are of no interest here. Errors in regular expressions
   will also be ignored*/



#include "agrepy.h"

/* First two service functions, the second of which is really only used
   during debugging  */

/* Add a new match to the list, i.e. pair of integers to array;
   Because it is common for there to be no matches, allocation
   of the matchlist is delayed until actually needed at the cost
   of an additional NULL test for each addition */

int_pair_list * add_ends(int start, int end, int_pair_list *matches)
{
  if(matches == NULL)
    {
    matches = (int_pair_list *) malloc(sizeof(int_pair_list));
    matches -> npairs = 0;
    matches -> maxpairs = INITPAIRS;
    matches -> pairs = (int_pair *) malloc(INITPAIRS * sizeof(int_pair));
    }
  else if (++(matches -> npairs) == matches -> maxpairs)
    {
    matches -> maxpairs = (int) (INCRPAIRS * matches -> maxpairs);
    matches -> pairs = (int_pair *) realloc(matches -> pairs, matches -> maxpairs * sizeof(int_pair));
    }

  (matches ->pairs[matches -> npairs]).start = start;

#ifdef PYTHON
  (matches ->pairs[matches -> npairs]).end = end + 1;
#else
  (matches ->pairs[matches -> npairs]).end = end;
#endif

#ifdef DEBUG
  printf("Added matches ->pairs[%d] start %d end %d\n",matches -> npairs, (matches ->pairs[matches -> npairs]).start, (matches ->pairs[matches -> npairs]).end);
#endif

  return(matches);
}

/* print a fragment of a string from start to end (inclusive)  */
void printnstring(register char *string, int start, int end)
{
  register char ch;
  register int i;

  for(i=start; i<=end; i++)
    {
    if((ch = string[i]) == '\0')
      return;
    putc(ch, stdout);
    }
}


int_pair_list *agrepy(char *pat, int patlen, char *text, int textlen,
		int gotoends, param_struct *parampt) 
{
  if(patlen <= SHORT_LONG)
    return(exec_sagrepy(pat, patlen, text, textlen, gotoends != 0, parampt));
  if(patlen <= MAXPATLEN)
    return(exec_lagrepy(pat, patlen, text, textlen, gotoends != 0, parampt));
  fprintf(stderr, "Pattern string must be no longer than %d\n", MAXPATLEN);
  return((int_pair_list *) NULL);
}

param_struct *compile(char* Pattern, int patlen, int NErrors)
{
  if(NErrors == 0)
    {
    fprintf(stderr, "agrepy.compile: The max number of errors must be 1 .. 8\n");
    fprintf(stderr, "\tThe min value (1) assumed\n");
    NErrors = 1;
    }
  else if(NErrors > 8)
    {
    fprintf(stderr, "agrepy.compile: The max number of errors must be 1 .. 8\n");
    fprintf(stderr, "\tThe max value (8) assumed\n");
    NErrors = 8;
    }
  if(patlen <= SHORT_LONG)
    return((param_struct *) sagrepy_compile(Pattern, patlen, (signed char) NErrors));
  return((param_struct *) lagrepy_compile(Pattern, patlen, (signed char) NErrors));
}

#ifdef STANDALONE
int main(){
  FILE *infile;
#ifdef NOTINUSE
  char *Pattern = "Actinomycetaceae";
  char *Input_File_Name = "xxxy1";
  char *Pattern = "caggcctaacacatgcaagtc";
  char *Input_File_Name = "xxxy3";
  char *Pattern = "acgggcggtgtgtacaag";
  char *Input_File_Name = "xxxy4";
#endif
  char *Input_File_Name = "xxxy5"; 
  char *Pattern = "caggcctaacacatgcaagtc";
  int NErrors = 4;
  int patlen = strlen(Pattern);
  char Text[10000];
  param_struct *s = compile(Pattern, patlen, NErrors);
  int_pair_list *result_list;
  int i, textlen;

  if((infile = fopen(Input_File_Name, "r")) == NULL)
    {
    printf("Cannot open %s\n", Input_File_Name);
    exit(1);
    }
  while(fgets(Text, 10000, infile) != NULL)
    {
    textlen = strlen(Text);
    Text[--textlen] = '\0';
    printf("Input: %s\n ", Text);
    result_list = agrepy(Pattern, patlen, Text, textlen, FALSE, s);
    if(result_list != NULL)
      {
      for(i=0; i<= result_list -> npairs; i++)
	{
        printf("Pair at %d to %d: ", result_list -> pairs[i].start, result_list -> pairs[i].end);
	printnstring(Text, result_list -> pairs[i].start, result_list -> pairs[i].end);
        printf("\n");
	}
      }
   else
      printf("No matches\n");
    }
  return(0);
}
#endif
