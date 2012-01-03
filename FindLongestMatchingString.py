# -*- coding: utf-8 -*-

# ===========================
# Find longest maching string
# ===========================
#
# These functions find the longest matching string in another string.

# For approximate pattern matching, use the Python port of TRE. See
# http://hackerboss.com/approximate-regex-matching-in-python/ for more details.
# I modified the Python wrapper code to allow Unicode strings.
import tre

def find_approx_text(search_text, target_text, cost = None):
    print("Searching for '%s'" % search_text)
    # tre.LITERAL specifies that search_str is a literal search string, not
    # a regex.
    pat = tre.compile(search_text, tre.LITERAL)
    fz = tre.Fuzzyness(maxerr = cost) if cost else tre.Fuzzyness()
    match = pat.search(target_text, fz)
    # match.group()[0][0] contains the the index into the target string of the
    # first matched char
    begin_in_target, end_in_target = match.groups()[0]
    print("found '" + target_text[begin_in_target:end_in_target] + "'")
    
    # TRE picks the first match it finds, even if there is
    # more than one matck with identical error. So,
    # manually call it again with a substring to check.
    match_again = pat.search(target_text[end_in_target:], fz)
    if match_again and (match_again.cost <= match.cost):
        print('Multiple matches ' + str(match_again.groups()))
        return None, 0, 0
    else:
        return match, begin_in_target, end_in_target
            
# This routine finds the a substring in the target document which contains an exact,
# unique match for a substring taken from the source document, anchored at the
# search location in the source document.
#
# search_text
#   The text composing the entire source document in which the search
#   string resides
#
# search_loc
#   A location in the source document which should be found in the
#   target document
#
# target_text
#   The target document
#
# search_range
#   Range of characters about the search_loc in which to search.
#
# returns
#   An exactly matching location in the target document, or -1 if not found
#
# Method:
#
# #. Look for the best approximate match within the target document of the source 
#    substring composed of characters within a radius of the anchor.
#
#    * If no unique match if found, give up (for now -- this could be improved).
#
# #. Record this cost (the difference between the source and target substrings)
#    and the left and right search radii.
#    Perform all future searches only within the source and target substrings
#    found in this search.
#
# #. While the search radius to the left of the anchor > 0 and the cost > 0:
#
#    #. Decrease the left search radius by half and approximate search again.
#
#    #. If there are multiple matches, undo this search radius change and exit.
#       This is the lowest achievable cost.
#
#    #. If the cost has decreased, record this new cost and its associated left
#       search radius.
#
# #. Now, repeat this process for the right search radius.
#
# #. If the cost is zero, report the location in the target; otherwise, return
#    a failure to match.
def find_approx_text_in_target(search_text, search_loc, target_text):
    return -1
    search_range = 40
    # Choose a +/- search_range of chars to search in.
    begin = max(0, search_loc - search_range)
    end = min(len(search_text), search_loc + search_range)
    match, begin_in_target, end_in_target = find_approx_text(search_text[begin:end], target_text)
    # Shrink the string being matched until we get an exact match, run
    # out of chars, get a multiple match, or have no match
    while (match and search_range and match.cost > 0):        
        # Search by removing chars from left side of search string
        left_begin = begin + (search_loc - begin)/2
        if left_begin > begin:
            left_match, left_begin_in_target, left_end_in_target = \
              find_approx_text(search_text[left_begin:end], target_text, match.cost)
        else:
            left_match = None
            
        # Search by removing chars from right side of search string
        right_end = search_loc + (end - search_loc)/2
        if right_end < end:
            right_match, right_begin_in_target, right_end_in_target = \
              find_approx_text(search_text[begin:right_end], target_text, match.cost)
        else:
            right_match = None
            
        # Choose the best
        if left_match:
            if right_match and right_match.cost < left_match.cost:
                match, begin_in_target, end_in_target = \
                  right_match, right_begin_in_target, right_end_in_target
                end = right_end
            else:
                match, begin_in_target, end_in_target = \
                  left_match, left_begin_in_target, left_end_in_target
                begin = left_begin
        else:
            match, begin_in_target, end_in_target = \
              right_match, right_begin_in_target, right_end_in_target
            end = right_end
            
    # Fail on no matches
    if not match:
        print('No matches.\n')
        return -1
    # A zero-cost match is an exact match
    if (match.cost == 0):
        # offset from that to pinpoint where in this string we want.
        match_len = search_loc - begin
        print('succeeded.\n')
        return begin_in_target + match_len

