from collections import OrderedDict
import math
import heapq


def add_number_of_word_to_dic(posting_list, doc_id, word_number):
    i = 1
    while i < len(posting_list):
        if doc_id in posting_list[i]:
            posting_list[i][doc_id].append(word_number)
            return
        i += 1
    posting_list[0] += 1
    posting_list.append({doc_id: [word_number]})


def delete_marks(line):
    i = 0
    while i < len(line):
        if 32 < ord(line[i]) < 39 or 39 < ord(line[i]) < 45 or 57 < ord(line[i]) < 65 or 90 < ord(line[i]) < 96:
            line = line[:i] + line[i + 1:]
            i -= 1
        i += 1
    line = line.replace("،", "")
    line = line.replace("{", "")
    line = line.replace("}", "")
    line = line.replace("\n", "")
    line = line.replace("\t", "")
    line = line.replace("«", "")
    line = line.replace("»", "")
    line = line.replace("؟", "")
    line = line.replace("؛", "")
    line = line.replace(".", "")
    line = line.replace("/", "")
    return line


def normalization(word):
    if word.endswith("تر"):
        word = word[:-2]
    if word.endswith("ترین"):
        word = word[:-4]
    if word.endswith("ها"):
        word = word[:-2]
    if word.endswith("های"):
        word = word[:-3]
    if word.endswith("‌ای"):
        word = word[:-3]
    if word.startswith("می‌"):
        word = word[3:]
    if word.startswith("نمی‌"):
        word = word[4:]
    word = word.replace("۱", "1")
    word = word.replace("۲", "2")
    word = word.replace("۳", "3")
    word = word.replace("۴", "4")
    word = word.replace("۵", "5")
    word = word.replace("۶", "6")
    word = word.replace("۷", "7")
    word = word.replace("۸", "8")
    word = word.replace("۹", "9")
    word = word.replace("۰", "0")
    word = word.replace("آ", "ا")
    return word


def has_same_start_6chars(word, dic_words):
    for target in dic_words:
        i = 0
        counter = 0
        while i < len(word) and i < len(target):
            if word[i] == target[i]:
                counter += 1
            i += 1
        if counter > 5:
            return True, target
    return False, None


def has_same_end_6chars(word, dic_words):
    for target in dic_words:
        i = len(word) - 1
        j = len(target) - 1
        counter = 0
        while -1 < i and -1 < j:
            if word[i] == target[j]:
                counter += 1
            i -= 1
            j -= 1
        if counter > 5:
            return True, target
    return False, None


def construct_champion_list(dic):
    final_dic = {}

    for k in dic:
        if dic[k][0] >= r:

            docs_with_weight = calculate_list_tf_idf(k, dic[k])
            # create max_heap
            heap = [(-value, key) for key, value in docs_with_weight.items()]
            max_heap = heapq.nsmallest(r, heap)
            max_heap = [key for value, key in max_heap]
            temp = [dic[k][0]]
            i = 1
            while i < len(dic[k]):
                if list(dic[k][i].keys())[0] in max_heap:
                    temp.append(dic[k][i])
                i += 1
            final_dic[k] = temp
        else:
            final_dic[k] = dic[k]

    # write back to file
    f = open("dics/champion_list_physics.txt", 'w+')
    for k in final_dic:
        text = k + '?!' + str(final_dic[k]) + '\n'
        f.write(text)
    f.close()


# {'hello': [6, {3: [1,6,8]}, {5, [3,6,5]}]}
def construct_positional_index(number_of_doc):
    tokens = {}

    for j in range(1, number_of_doc + 1):
        doc = "phase3/physics/" + str(j) + ".txt"
        f1 = open(doc)
        counter = 0
        for line in f1.readlines():
            # delete stop words and marks
            line = delete_marks(line)
            for word in line.split(" "):
                # Normalize words
                word = normalization(word)
                # delete half space
                word = word.replace("‌", "")
                counter += 1
                if word not in tokens:
                    t1 = has_same_end_6chars(word, tokens)
                    t2 = has_same_start_6chars(word, tokens)
                    if t1[0]:
                        if not tokens[t1[1]].__contains__(j):
                            add_number_of_word_to_dic(tokens[t1[1]], j, counter)

                    elif t2[0]:
                        if not tokens[t2[1]].__contains__(j):
                            add_number_of_word_to_dic(tokens[t2[1]], j, counter)
                    else:
                        tokens[word] = [1, {j: [counter]}]
                else:

                    add_number_of_word_to_dic(tokens[word], j, counter)

        f1.close()

    # delete most common words
    temp = []
    for i in tokens:
        if len(tokens[i]) > 0.79 * number_of_doc:
            temp.append(i)
    i = 0
    while i < len(temp):
        del tokens[temp[i]]
        i += 1

    # sort tokens
    od = OrderedDict(sorted(tokens.items()))

    # write back to file
    f = open("dics/dictionary_physics.txt", 'w+')
    final_dic = {}
    for k, v in od.items():
        final_dic[k] = v
        print(k, v)
        text = k + '?!' + str(v) + '\n'
        f.write(text)
    f.close()

    construct_champion_list(final_dic)

    return final_dic


def calculate_list_tf_idf(word, list_word):
    # list_word = dic[word]
    weight_doc = {}

    df = list_word[0]
    idf = math.log(total_docs / df, 10)
    i = 1
    while len(list_word) != 1 and i < len(list_word):
        doc_id = list(list_word[i].keys())[0]
        tf = len(list_word[i][doc_id])
        w = (1 + math.log(tf, 10)) * idf
        weight_doc[doc_id] = w
        i += 1
    return weight_doc


def query_single_word(word, dic):
    word = normalization(word)

    if word in dic:
        list_word = dic[word]
        # weight_doc = calculate_list_tf_idf(word, dic)
        return list_word  # , weight_doc

    temp = has_same_start_6chars(word, dic)
    if temp[0]:
        word = temp[1]
        list_word = dic[word]
        # weight_doc = calculate_list_tf_idf(word, dic)
        return list_word  # , weight_doc

    temp = has_same_end_6chars(word, dic)
    if temp[0]:
        word = temp[1]
        list_word = dic[word]
        # weight_doc = calculate_list_tf_idf(word, dic)
        return list_word  # , weight_doc
    return "No answer!"


def calculate_similarity(weight_query_words, weight_list):
    similarity_list = {}
    for i in weight_query_words:
        if i in weight_list:
            for j in weight_list[i]:
                if j in similarity_list:
                    similarity_list[j][0] += weight_list[i][j] * weight_query_words[i]
                    similarity_list[j][1] += weight_list[i][j] ** 2
                    similarity_list[j][2] += 1
                else:
                    # = [ a.b , a^2 ]
                    similarity_list[j] = [weight_list[i][j] * weight_query_words[i], weight_list[i][j] ** 2, 1]
    # print(similarity_list)

    # calculate |b|
    b2 = 0
    for i in weight_query_words:
        b2 += weight_query_words[i] ** 2
    b = math.sqrt(b2)

    result = {}
    for i in similarity_list:
        result[i] = similarity_list[i][0] / (math.sqrt(similarity_list[i][1]) * b)
    return result


def remove_docs_with_few_words(words, pos_list):
    accumulate_doc = {}
    for k in pos_list:
        i = 1
        while i < len(pos_list[k]):
            if list(pos_list[k][i].keys())[0] in accumulate_doc:
                accumulate_doc[list(pos_list[k][i].keys())[0]] += 1
            else:
                accumulate_doc[list(pos_list[k][i].keys())[0]] = 1
            i += 1
    # print(accumulate_doc)

    for i in accumulate_doc:
        if len(words) > 2 and accumulate_doc[i] / len(words) < 0.6:
            for k in pos_list:
                j = 1
                while j < len(pos_list[k]):
                    if list(pos_list[k][j].keys())[0] == i:
                        del pos_list[k][j]
                        j -= 1
                    j += 1
    return pos_list


def test_IR(word, champ_dic):

    # single word query
    if len(word.split(" ")) == 1:
        answer = query_single_word(word, champ_dic)
        if type(answer) is list:
            weight_doc = calculate_list_tf_idf(word, champ_dic[word])
            # print(answer[0], '\n', answer[1])
            # create max_heap
            heap = [(-value, key) for key, value in weight_doc.items()]
            max_heap = heapq.nsmallest(k, heap)
            max_heap = [(key, -value) for value, key in max_heap]
            return max_heap
        else:
            return answer

    # multi words query
    else:

        s = word.split(" ")

        # calculate tf of query words
        tf_query_words = {}
        for i in s:
            if i in tf_query_words:
                tf_query_words[i] += 1
            else:
                tf_query_words[i] = 1

        # calculate weight of query words
        weight_query_words = {}
        for i in tf_query_words:
            if i in champ_dic:
                weight_query_words[i] = (1 + math.log(tf_query_words[i], 10)) * math.log(total_docs / champ_dic[i][0],
                                                                                         10)
            else:
                weight_query_words[i] = 0
        # print(weight_query_words)

        position_champ = {}

        # get position list of query words
        i = 0
        while i < len(s):
            answer_champ = query_single_word(s[i], champ_dic)
            if type(answer_champ) is list:
                position_champ[s[i]] = answer_champ
            i += 1

        # print(position_list)

        # remove docs with few words of query
        position_champ = remove_docs_with_few_words(s, position_champ)
        # calculate combined list of word's weight
        weight_champ_list = {}
        for i in s:
            if i in position_champ:
                w = calculate_list_tf_idf(i, position_champ[i])
                if w != {}:
                    weight_champ_list[i] = w
        # print(weight_list)

        # calculate similarity of query and dictionary
        result = calculate_similarity(weight_query_words, weight_champ_list)
        # create max_heap
        heap = [(-value, key) for key, value in result.items()]
        max_heap = heapq.nsmallest(k, heap)
        max_heap = [(key, -value) for value, key in max_heap]

        return max_heap


def create_posting_list_from_file(line):
    posting_list = []
    line = line.split("{")
    posting_list.append(int(line[0].replace("[", "").replace(", ", "")))
    i = 1
    while i < len(line):
        line[i] = line[i].split("}")[0]
        s = line[i].split(":")
        index = {int(s[0]): []}
        word_numbers = s[1].replace("]", "").replace("[", "").split(",")
        for j in word_numbers:
            index[int(s[0])].append(int(j))
        i += 1
        posting_list.append(index)
    return posting_list


def load_positional_dic():
    f = open("dictionary.txt")
    dic = {}
    for line in f.readlines():
        line = line.replace("\n", "")
        splited = line.split("!")

        if splited[0].__contains__("?"):

            splited[0] = splited[0].replace(" ", "")
            splited[0] = splited[0].replace("?", "")
            dic[splited[0]] = create_posting_list_from_file(splited[1])
        else:
            splited[1] = splited[1].replace(" ", "")
            splited[1] = splited[1].replace("?", "")
            dic[splited[1]] = create_posting_list_from_file(splited[0])
    f.close()

    f = open("champion_list.txt")
    champ_dic = {}
    for line in f.readlines():
        line = line.replace("\n", "")
        splited = line.split("!")

        if splited[0].__contains__("?"):

            splited[0] = splited[0].replace(" ", "")
            splited[0] = splited[0].replace("?", "")
            champ_dic[splited[0]] = create_posting_list_from_file(splited[1])
        else:
            splited[1] = splited[1].replace(" ", "")
            splited[1] = splited[1].replace("?", "")
            champ_dic[splited[1]] = create_posting_list_from_file(splited[0])
    f.close()
    return dic, champ_dic

def test_phase_2():
    dic, champ_dic = load_positional_dic()

    word = input()

    answer = test_IR(word, champ_dic)
    print(answer)
    if answer is not None and len(answer) < k:
        answer_total = test_IR(word, dic)
        # remove docs that was available in answer list
        for i in answer:
            j = 0
            while j < len(answer_total):
                if i[0] == answer_total[j][0]:
                    del answer_total[j]
                    j -= 1
                j += 1
        print(answer_total)


def load_positional_dic_cluster(name):
    s = 'dics/dictionary_'+name+'.txt'
    f = open(s)
    dic = {}
    for line in f.readlines():
        line = line.replace("\n", "")
        splited = line.split("!")

        if splited[0].__contains__("?"):

            splited[0] = splited[0].replace(" ", "")
            splited[0] = splited[0].replace("?", "")
            dic[splited[0]] = create_posting_list_from_file(splited[1])
        else:
            splited[1] = splited[1].replace(" ", "")
            splited[1] = splited[1].replace("?", "")
            dic[splited[1]] = create_posting_list_from_file(splited[0])
    f.close()

    s = 'dics/champion_list_' + name + '.txt'
    f = open(s)
    champ_dic = {}
    for line in f.readlines():
        line = line.replace("\n", "")
        splited = line.split("!")

        if splited[0].__contains__("?"):

            splited[0] = splited[0].replace(" ", "")
            splited[0] = splited[0].replace("?", "")
            champ_dic[splited[0]] = create_posting_list_from_file(splited[1])
        else:
            splited[1] = splited[1].replace(" ", "")
            splited[1] = splited[1].replace("?", "")
            champ_dic[splited[1]] = create_posting_list_from_file(splited[0])
    f.close()
    return dic, champ_dic

def calculate_center_of_clusters(n, cluster_name):
    # load dic
    name = 'dics/dictionary_' + cluster_name + '.txt'
    f = open(name)
    dic = {}
    for line in f.readlines():
        line = line.replace("\n", "")
        splited = line.split("!")

        if splited[0].__contains__("?"):

            splited[0] = splited[0].replace(" ", "")
            splited[0] = splited[0].replace("?", "")
            dic[splited[0]] = create_posting_list_from_file(splited[1])
        else:
            splited[1] = splited[1].replace(" ", "")
            splited[1] = splited[1].replace("?", "")
            dic[splited[1]] = create_posting_list_from_file(splited[0])
    f.close()
    words_center_of_cluster = []
    for k in dic:
        sum = dic[k][0]
        i = 1
        while i < len(dic[k]):
            doc_id = list(dic[k][i].keys())[0]
            sum += len(dic[k][i][doc_id])
            i += 1

        if sum >= n:
            words_center_of_cluster.append(k)
    print(len(words_center_of_cluster), words_center_of_cluster)

    # write back to file
    s = "centers/centers_" + cluster_name + ".txt"
    f = open(s, 'w+')

    for k in words_center_of_cluster:

        text = k + ','
        f.write(text)
    f.close()


def load_center_of_clusters(name):
    s = 'centers/centers_' + name+'.txt'
    f = open(s)
    words = f.readline().split(',')
    f.close()
    return words

def test_phase_3():
    word = input()
    value_max = 0
    category = 'health'
    categories = ['health', 'history', 'physics', 'math', 'technology']
    for i in categories:
        words_center = load_center_of_clusters(i)
        value = 0
        for j in word.split(" "):
            if j in words_center:
                value += 1

        if value >= value_max:
            value_max = value
            category = i

    print(category)
    dic, champ_dic = load_positional_dic_cluster(category)

    answer = test_IR(word, champ_dic)
    print(answer)
    if answer is not None and len(answer) < k:
        answer_total = test_IR(word, dic)
        # remove docs that was available in answer list
        for i in answer:
            j = 0
            while j < len(answer_total):
                if i[0] == answer_total[j][0]:
                    del answer_total[j]
                    j -= 1
                j += 1
        print(answer_total)

if __name__ == "__main__":
    total_docs = 100
    k = 7
    r = 5
    ##### ATTENTION ###########
    ###### Do not forget to set the name of dictionary file and its champion list #######
    # construct_positional_index(60)


    ###### calculate center of clusters
    # least_number_of_docs_have_that_word = 40
    # cluster_name = 'physics'
    # calculate_center_of_clusters(least_number_of_docs_have_that_word, cluster_name)

    # for test phase 2
    # test_phase_2()

    # test phase 3
    test_phase_3()
