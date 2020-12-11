from collections import OrderedDict


def delete_marks(line):
    i = 0
    while i < line:
        if 32 < ord(line[i]) < 39 or 39 < ord(line[i]) < 45 or 57 < ord(line[i]) < 65 or 90 < ord(line[i]) < 96:
            del line[i]
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


def construct_inverted_index():
    tokens = {}

    for j in range(1, 11):
        doc = "sampleDoc/" + str(j) + ".txt"
        f1 = open(doc)
        for line in f1.readlines():
            # delete stop words and marks
            line = delete_marks(line)
            for word in line.split(" "):
                # Normalize words
                word = normalization(word)
                # delete half space
                word = word.replace("‌", "")
                if word not in tokens:
                    t = has_same_end_6chars(word, tokens)
                    if t[0]:
                        if not tokens[t[1]].__contains__(j):
                            tokens[t[1]].append(j)
                    t = has_same_start_6chars(word, tokens)
                    if t[0]:
                        if not tokens[t[1]].__contains__(j):
                            tokens[t[1]].append(j)
                    else:
                        tokens[word] = [j]
                elif not tokens[word].__contains__(j):
                    tokens[word].append(j)

        f1.close()

    # delete most common words
    temp = []
    for i in tokens:
        if len(tokens[i]) > 7:
            temp.append(i)
    i = 0
    while i < len(temp):
        del tokens[temp[i]]
        i += 1

    # sort tokens
    od = OrderedDict(sorted(tokens.items()))
    f = open("result.txt", 'w+')

    final_dic = {}
    for k, v in od.items():
        final_dic[k] = v
        print(k, v)
        text = k + ':' + str(v) + '\n'
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
        for i in s:
            docs = query_single_word(i, dictionary)
            if docs != "No answer!":
                for j in docs:
                    if j not in results:
                        results[j] = 1
                    else:
                        results[j] += 1
        # search the query without space
        word = word.replace(" ", "")
        docs = query_single_word(word, dictionary)
        if docs != "No answer!":
            for j in docs:
                if j not in results:
                    results[j] = 1
                else:
                    results[j] += 1
        results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
        print(results)


def load_dic():
    f = open("result.txt")
    dic = {}
    for line in f.readlines():
        splited = line.split(":")
        if splited[0].__contains__("["):
            splited[0] = splited[0].rstrip('\n').replace(']', "").replace('[', "").replace(" ", "")
            listed = []
            for i in splited[0].split(","):
                listed.append(i)
            dic[splited[1]] = listed
        else:
            splited[1] = splited[1].rstrip('\n').replace(']', "").replace('[', "").replace(" ", "")
            listed = []
            for i in splited[1].split(","):
                listed.append(i)
            dic[splited[0]] = listed
    f.close()
    return dic


if __name__ == "__main__":
    dic = load_dic()
    test_IR(dic)
