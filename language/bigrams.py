from utils import get_word_counts, show_in_order
from collections import defaultdict, Counter
from string import ascii_lowercase

VOWELS = 'aeiou'

def get_bigram_frequencies(word_counts):
    bigrams = defaultdict(int)

    for word, count in word_counts.items():
        first_character = word[0]
        for second_character in word[1:]:
            bigrams[first_character + second_character] += count
            first_character = second_character

    return bigrams


def find_word_containing_substring(words, substring):
    for word in words:
        if substring in "^{}$".format(word):
            return word


def find_words_containing_substring(words, substring):
    return [word for word in words if substring in word]


def get_bigram_dictionary(word_counts):
    characters = ascii_lowercase + "^"
    bigrams = {character: defaultdict(int) for character in characters}

    for word, frequency in word_counts.items():
        first_character = "^"
        for second_character in word:
            bigrams[first_character][second_character] += frequency
            first_character = second_character
        bigrams[first_character]["$"] += frequency

    return bigrams


def find_missing_bigrams(bigrams):
    character_counts = defaultdict(int)
    bigram_count = 0

    for first_character in ascii_lowercase:
        for second_character in ascii_lowercase:
            bigram = first_character + second_character
            if not bigrams.get(bigram):
                character_counts[bigram[0]] += 1
                character_counts[bigram[1]] += 1
                bigram_count += 1
                if first_character in VOWELS or second_character in VOWELS:
                    print(bigram)

    for character, count in sorted(character_counts.items(), key=lambda x: -x[1]):
        print(character, count)

    print(bigram_count)


def write_most_disproportionate_bigrams(bigram_dict):
    bigrams = {}

    for first_character, second_characters in bigram_dict.items():
        if first_character == '^':
            continue
        for second_character, proportion in second_characters.items():
            if second_character == '$':
                continue
            bigrams[first_character + second_character] = proportion

    for bigram, proportion in sorted(bigrams.items(), key=lambda x: -x[1])[:10]:
        print(bigram, proportion * 100)


def strip_pseduo_bigrams(bigram_dict):
    filtered_bigrams = dict()

    for first_character, second_characters in bigram_dict.items():
        if first_character == '^':
            continue

        frequencies = dict()
        for second_character, frequency in second_characters.items():
            if second_character != '$':
                frequencies[second_character] = frequency 
        
        filtered_bigrams[first_character] = frequencies

    return filtered_bigrams


def normalise_bigram_dict(bigram_dict):
    # bigram_dict = strip_pseduo_bigrams(bigram_dict)
    normalised_bigram_dict = dict()

    for first_character, second_characters in bigram_dict.items():
        total = sum(second_characters.values())
        frequencies = dict()

        for second_character, frequency in second_characters.items():
            frequencies[second_character] = frequency / total

        normalised_bigram_dict[first_character] = frequencies

    return normalised_bigram_dict


def get_cluster_chain_dictionary(words, clusters):
    max_length = max(len(cluster) for cluster in clusters)
    clusters += list(ascii_lowercase)
    clusters.append("^")
    cluster_chain = {cluster: defaultdict(int) for cluster in clusters}
    all_clusters = set()

    for word, frequency in words.items():
        first_cluster = "^"
        current_index = 0
        while current_index < len(word):
            block_size = max_length

            # Check for block of letters in cluster with decreasing block size
            while word[current_index: current_index + block_size] not in clusters:
                block_size -= 1

            # Add this second cluster to the dictionary
            second_cluster = word[current_index: current_index + block_size]
            cluster_chain[first_cluster][second_cluster] += frequency
            all_clusters.add(second_cluster)
            first_cluster = second_cluster
            current_index += block_size
        cluster_chain[first_cluster]["$"] += frequency

    # Strip out any clusters that can't be reached
    dict_size = 0
    for first_cluster, second_clusters in cluster_chain.items():
        dict_size += len(second_clusters)
        if first_cluster != "^" and first_cluster not in all_clusters:
            print("Remove", first_cluster)
            del cluster_chain[first_cluster]

    print(dict_size)

    return cluster_chain


def convert_words_to_vowel_and_consonant_blocks(words):
    """
    Given a list of words, return a dict that maps words to a
    tuple of vowel and consonant blocks.
    block['block'] = ('bl', 'o', 'ck')
    """
    word_blocks = dict()

    for word in words:
        blocks = list()
        current_characters = word[0]
        is_vowel = current_characters in VOWELS

        for character in word[1:]:
            if (character in VOWELS) == is_vowel:
                # Same letter type so extend block
                current_characters += character
            else:
                # Different letter type, so add block and create a new one
                blocks.append(current_characters)
                current_characters = character
                is_vowel = not is_vowel

        blocks.append(current_characters)
        word_blocks[word] = tuple(blocks)

    return word_blocks


def count_blocks(blocks, word_frequencies):
    block_frequencies = defaultdict(int)

    for word, blocks in blocks.items():
        frequency = word_frequencies[word]
        for block in blocks:
            block_frequencies[block] += frequency

    return block_frequencies


if __name__ == '__main__':
    import os
    word_counts = get_word_counts(os.path.join('word_lists', 'filtered_word_counts.txt'))
    words = word_counts.keys()
    bigrams = get_bigram_frequencies(word_counts)
    bigram_dict = get_bigram_dictionary(word_counts)

    # show_in_order(bigrams)
    # total_bigrams = sum(count for count in bigrams.values())
    # print(total_bigrams)

    # for bigram, count in sorted(bigrams.items(), key=lambda item: item[1])[:10]:
    #     print(bigram, count, find_words_containing_substring(words, bigram))

    # Top 40 bigrams
    # top_bigrams = [item for item, count in sorted(bigrams.items(), key=lambda item: item[1])[:40]]
    # letter_counts = Counter("".join(top_bigrams))
    # print(letter_counts)

    # find_missing_bigrams(bigrams)

    # bigram_dict = normalise_bigram_dict(bigram_dict)
    # write_most_disproportionate_bigrams(bigram_dict)

    word_to_blocks = convert_words_to_vowel_and_consonant_blocks(words)
    block_counts = count_blocks(word_to_blocks, word_counts)

    show_in_order(block_counts, 10)

    # get_cluster_chain_dictionary(words, clusters)
