INPUTS = 'inputs'
DOCS = 'docs'
RETURN_TYPE = 'return_type'


def sort_matches_by_scores(func):
    """Method to ensure that return docs have matches sorted by score"""

    def wrapper(*args, **kwargs):
        from docarray import DocList
        res = func(*args, **kwargs)
        obj = args[0]
        if isinstance(res, DocList):
            for doc in res:
                matches = doc.matches
                scores = doc.scores
                # Combine the lists into pairs
                pairs = zip(scores, matches)

                # Sort the pairs based on the values of list1
                sorted_pairs = sorted(pairs, key=lambda x: x[0], reverse=obj.reverse_score_order)

                # Separate the sorted pairs into separate lists
                sorted_scores, sorted_matches = zip(*sorted_pairs)
                doc.matches = sorted_matches
                doc.scores = sorted_scores
        else:
            matches = res.matches
            scores = res.scores
            # Combine the lists into pairs
            pairs = zip(scores, matches)

            # Sort the pairs based on the values of list1
            sorted_pairs = sorted(pairs, key=lambda x: x[0], reverse=obj.reverse_score_order)

            # Separate the sorted pairs into separate lists
            sorted_scores, sorted_matches = zip(*sorted_pairs)
            res.matches = sorted_matches
            res.scores = sorted_scores
        return res

    return wrapper
