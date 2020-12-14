from collections import OrderedDict


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


# {'hello': [6, {3: [1,6,8]}, {5, [3,6,5]}]}
def construct_positional_index(number_of_doc):
    tokens = {}

    for j in range(1, number_of_doc + 1):
        doc = "sampleDoc/" + str(j) + ".txt"
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
        if len(tokens[i]) > 0.75 * number_of_doc:
            temp.append(i)
    i = 0
    while i < len(temp):
        del tokens[temp[i]]
        i += 1

    # sort tokens
    od = OrderedDict(sorted(tokens.items()))

    # write back to file
    f = open("dictionary.txt", 'w+')
    final_dic = {}
    for k, v in od.items():
        final_dic[k] = v
        print(k, v)
        text = k + '?!' + str(v) + '\n'
        f.write(text)
    f.close()
    return final_dic


def query_single_word(word, dic):
    word = normalization(word)

    if word in dic:
        return dic[word]
    temp = has_same_start_6chars(word, dic)
    if temp[0]:
        return dic[temp[1]]
    temp = has_same_end_6chars(word, dic)
    if temp[0]:
        return dic[temp[1]]
    return "No answer!"


def test_IR(dictionary):
    word = input()
    if len(word.split(" ")) == 1:
        print(query_single_word(word, dictionary))
    else:
        results = {}
        s = word.split(" ")
        i = 0
        while i < len(s):
            docs = query_single_word(s[i], dictionary)
            if docs != "No answer!":
                results[s[i]] = docs
            i += 1

        # print(results)

        accumulation = {}
        for i in results:
            k = 1
            while k < len(results[i]):
                temp = list(results[i][k].keys())[0]
                if temp in accumulation:
                    accumulation[temp] += 1
                else:
                    accumulation[temp] = 1
                k += 1

        accumulation = dict(sorted(accumulation.items(), key=lambda item: item[1], reverse=True))
        if accumulation != {}:
            print(accumulation)
        else:
            print("No answer!")


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
    return dic


if __name__ == "__main__":
    construct_positional_index(10)
    # dic = load_positional_dic()
    # test_IR(dic)
