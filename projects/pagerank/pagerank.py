import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    #Create a dictionairy that will have the variables added
    probabilities = {}
    #For all pages in corpus set probability to, (1-damping_factor)(1/Number of pages)
    for key in corpus:
        probabilities[key] =(1-damping_factor) /len(corpus)
    #For pages linked to current page, add damping_factor(1/number of linked pages)
    linked_pages = corpus[page]
    if linked_pages:
        for linked_page in linked_pages:
            probabilities[linked_page] += damping_factor / (len(linked_pages))
    else:
        for key in corpus:
            probabilities[key] += damping_factor / len(corpus)

    return probabilities

    


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_visited_count = {page: 0 for page in corpus}
    current_page = random.choice(list(corpus.keys()))
    page_visited_count[current_page] += 1

    for i in range(1, n):
        current_page_probability = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(
            list(current_page_probability.keys()), 
            weights=current_page_probability.values(), 
            k = 1
        )[0]
        page_visited_count[current_page] +=1    
    
    total_visits = sum(page_visited_count.values())
    return {page : count / total_visits for page, count in page_visited_count.items()}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probability = {page: 1/len(corpus) for page in corpus}

    while True:
        adjustments = []
        for key in corpus:
            original_probability = probability[key]
            sum_of_linking_pages_probabilities = 0
            for page in corpus:
                if len(corpus[page]) == 0:
                    sum_of_linking_pages_probabilities += probability[page] / len(corpus)
                elif key in corpus[page]:
                    sum_of_linking_pages_probabilities += probability[page] / len(corpus[page])
            
            probability[key] = ((1-damping_factor) / len(corpus)) + (damping_factor * sum_of_linking_pages_probabilities)

            new_probability = probability[key]
            adjustments.append(abs(new_probability-original_probability))

        if max(adjustments) > 0.001:
            continue
        else:
            break
        
    return probability
                
            



if __name__ == "__main__":
    main()
