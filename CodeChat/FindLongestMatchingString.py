# -*- coding: utf-8 -*-

# ============================
# Find longest matching string
# ============================
#
# The find_approx_text_in_target_ function in this module searches a target string for the best match to characters about an anchor point in a source string. In particular, it first locates a block of target text which forms the closest approximate match for source characters about the anchor. Then, it looks for the (almost) longest possible exact match between source characters about the anchor and the block of target text found in the first step.
#
# Implementation
# =============================================================================
#
# For approximate pattern matching, this module uses the Python port of TRE. See  http://hackerboss.com/approximate-regex-matching-in-python/ for more details. I modified the Python wrapper code to allow Unicode strings.
import tre

# .. _find_approx_text:
#
# find_approx_text
# ------------------------------------------------------------------------------
# The find_approx_text function performs a single approximate match; find_approx_text_in_target_ calls this repeatedly. Its parameters:
#
# search_text
#   Text to search for
#
# target_text
#   Text in which to find the search_text
#
# cost
#   Maximum allowable cost for an approximate match.
#
# Return value:
#   - If there is no unique value, (None, 0, 0)
#   - Otherwise, it returns (match, begin_in_target, end_in_target) where:
#
#     match
#       A TRE match object.
#
#     begin_in_target
#       The index into the target string at which the approximate match begins.
#
#     end_in_target
#       The index into the target string at which the approximate match ends.
def find_approx_text(search_text, target_text, cost = None):
    # tre.LITERAL specifies that search_str is a literal search string, not
    # a regex.
    pat = tre.compile(search_text, tre.LITERAL)
    fz = tre.Fuzzyness(maxerr = cost) if cost else tre.Fuzzyness()
    match = pat.search(target_text, fz)
    # match.group()[0][0] contains the the index into the target string of the
    # first matched char
    begin_in_target, end_in_target = match.groups()[0]
    
    # TRE picks the first match it finds, even if there is
    # more than one matck with identical error. So,
    # manually call it again with a substring to check.
    match_again = pat.search(target_text[end_in_target:], fz)
    if match_again and (match_again.cost <= match.cost):
#        print('Multiple matches ' + str(match_again.groups()))
        return None, 0, 0
    else:
#        print(search_text + '\n' + target_text[begin_in_target:end_in_target])
        return match, begin_in_target, end_in_target

# .. _find_approx_text_in_target:
#
# find_approx_text_in_target
# ==========================
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
# #. Look for the best approximate match within the target document of the source substring composed of characters within a radius of the anchor.
#
#    * If no unique match if found, give up (for now -- this could be improved).
#
# #. Record this cost (the difference between the source and target substrings) and the left and right search radii. Perform all future searches only within the source and target substrings found in this search.
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
# #. If the cost is zero, report the location in the target; otherwise, return a failure to match.
def find_approx_text_in_target(search_text, search_anchor, target_text):
    search_range = 20
    step_size = 4
    # #. Look for the best approximate match within the target document of the source substring composed of characters within a radius of the anchor.
    #
    # First, choose a radius of chars about the anchor to search in.
    begin = max(0, search_anchor - search_range)
    end = min(len(search_text), search_anchor + search_range)
    # Empty documents are easy to search
    if end <= begin:
        return 0
    # Look for a match; record left and right search radii
    match, begin_in_target, end_in_target = find_approx_text(search_text[begin:end], target_text)
    #    * If no unique match if found, give up (for now -- this could be improved).
    if not match:
#        print("No unique match found.")
        return -1
    
    # #. Record this cost (the difference between the source and target substrings). Perform all future searches only within the source and target substrings found in this search.
    min_cost = match.cost
    min_cost_begin = begin
    min_cost_end = end
    
    # For an exact match, need to define this, since the while loops won't.
    # We're 0 characters forward from the begin_in_target point before we
    # do any additional search refinements.
    begin_in_target_substr = 0

    # #. While the search radius to the left of the anchor > 0 and the cost > 0:
#    print('Searching right radius')
    while (end > search_anchor) and (min_cost > 0):

        #    #. Decrease the left search radius by half and approximate search again.
        #
        # Note that when (end - search_anchor)/2 == 0 when
        # end = search_anchor + 1, causing infinite looping. The max fixes
        # this case.
        end -= max((end - search_anchor) - step_size, 1)
        match, begin_in_target_substr, end_in_target_substr = \
            find_approx_text(search_text[begin:end], 
                             target_text[begin_in_target:end_in_target])

        #    #. If there are multiple matches, undo this search radius change and exit.
        #       This is the lowest achievable cost.
        if not match:
            break
        
        #    #. If the cost has decreased, record this new cost and its associated left
        #       search radius.
        if match.cost < min_cost:
            min_cost = match.cost
            min_cost_end = end

    # #. Repeat the above loop for the right search radius
#    print('Searching left radius')
    while (begin < search_anchor) and (min_cost > 0):

        #    #. Decrease the right search radius by half and approximate search again.
        begin += max((search_anchor - begin) - step_size, 1)
        match, begin_in_target_substr, end_in_target_substr = \
            find_approx_text(search_text[begin:min_cost_end],
                             target_text[begin_in_target:end_in_target])

        #    #. If there are multiple matches, undo this search radius change and exit.
        #       This is the lowest achievable cost.
        if not match:
            break
        
        #    #. If the cost has decreased, record this new cost and its associated left
        #       search radius.
        if match.cost < min_cost:
            min_cost = match.cost
            min_cost_begin = begin

    # #. If the cost is zero, report the location in the target; otherwise, return a failure to match.
    if min_cost > 0:
#        print('Failed -- no exact match (cost was %d)' % min_cost)
        return -1
    else:
##        print('''
##begin_in_target %d
##begin_in_target_substr %d
##search_anchor %d
##min_cost_begin %d''' % (begin_in_target, begin_in_target_substr, search_anchor, min_cost_begin))
        return begin_in_target + begin_in_target_substr + (search_anchor - min_cost_begin)


if __name__ == '__main__':
    from CodeChatTest import main
    main()
