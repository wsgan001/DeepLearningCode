import random, operator
import  numpy as np
from theano import config

def build_vocab():
    code, vocab = int(0), {}
    vocab['UNKNOWN'] = code
    code += 1
    for line in open('QAcorpus/train'):
        items = line.strip().split(' ')
        for i in range(2, 3):
            for word in items[i].split('_'):
                if len(word) <= 0:
                    continue
                if not word in vocab:
                    vocab[word] = code
                    code += 1
    return vocab

def load_vectors():
    vectors = {}
    for line in open('QAcorpus/vectors.nobin'):
        items = line.strip().split(' ')
        if len(items[0]) <= 0:
            continue
        vec = []
        for i in range(1, 101):
            vec.append(float(items[i]))
        vectors[items[0]] = vec
    return vectors

def load_word_embeddings(vocab, dim):
    vectors = load_vectors()
    embeddings = [] #brute initialization
    for i in range(0, len(vocab)):
        vec = []
        for j in range(0, dim):
            vec.append(0.01)
        embeddings.append(vec)
    for word, code in vocab.items():
        if word in vectors:
            embeddings[code] = vectors[word]
    return np.array(embeddings, dtype='float32')

#be attention initialization of UNKNNOW
def encode_sent(vocab, string, size):
    x, m = [], []
    words = string.split('_')
    for i in range(0, size):
        if words[i] in vocab:
            x.append(vocab[words[i]])
        else:
            x.append(vocab['UNKNOWN'])
        if words[i] == '<a>': #TODO
            m.append(1) #fixed sequence length, else use 0
        else:
            m.append(1)
    return x, m

def load_train_list():
    trainList = []
    for line in open('QAcorpus/train'):
        items = line.strip().split(' ')
        if items[0] == '1':
            trainList.append(line.strip().split(' '))
    return trainList

def load_test_list():
    testList = []
    for line in open('QAcorpus/test1'):
        testList.append(line.strip().split(' '))
    return testList

def load_data(trainList, vocab, batch_size):
    train_1, train_2, train_3 = [], [], []
    mask_1, mask_2, mask_3 = [], [], []
    counter = 0
    while True:
        pos = trainList[random.randint(0, len(trainList)-1)]
        neg = trainList[random.randint(0, len(trainList)-1)]
        if pos[2].startswith('<a>') or pos[3].startswith('<a>') or neg[3].startswith('<a>'):
            #print 'empty string ......'
            continue
        x, m = encode_sent(vocab, pos[2], 100)
        train_1.append(x)
        mask_1.append(m)
        x, m = encode_sent(vocab, pos[3], 100)
        train_2.append(x)
        mask_2.append(m)
        x, m = encode_sent(vocab, neg[3], 100)
        train_3.append(x)
        mask_3.append(m)
        counter += 1
        if counter >= batch_size:
            break
    return np.transpose(np.array(train_1, dtype=config.floatX)), np.transpose(np.array(train_2, dtype=config.floatX)), np.transpose(np.array(train_3, dtype=config.floatX)), np.transpose(np.array(mask_1, dtype=config.floatX)) , np.transpose(np.array(mask_2, dtype=config.floatX)), np.transpose(np.array(mask_3, dtype=config.floatX))

def load_data_val(testList, vocab, index, batch_size):
    x1, x2, x3, m1, m2, m3 = [], [], [], [], [], []
    for i in range(0, batch_size):
        true_index = index + i
        if true_index >= len(testList):
            true_index = len(testList) - 1
        items = testList[true_index]
        x, m = encode_sent(vocab, items[2], 100)
        x1.append(x)
        m1.append(m)
        x, m = encode_sent(vocab, items[3], 100)
        x2.append(x)
        m2.append(m)
        x, m = encode_sent(vocab, items[3], 100)
        x3.append(x)
        m3.append(m)
    return np.transpose(np.array(x1, dtype=config.floatX)), np.transpose(np.array(x2, dtype=config.floatX)), np.transpose(np.array(x3, dtype=config.floatX)), np.transpose(np.array(m1, dtype=config.floatX)) , np.transpose(np.array(m2, dtype=config.floatX)), np.transpose(np.array(m3, dtype=config.floatX))

def validation(validate_model, testList, vocab, batch_size):
    index, score_list = int(0), []
    while True:
        x1, x2, x3, m1, m2, m3 = load_data_val(testList, vocab, index, batch_size)
        batch_scores, nouse = validate_model(x1, x2, x3, m1, m2, m3)
        for score in batch_scores:
            score_list.append(score)
        index += batch_size
        if index >= len(testList):
            break
        print 'Evaluation ' + str(index)
    sdict, index = {}, int(0)
    for items in testList:
        qid = items[1].split(':')[1]
        if not qid in sdict:
            sdict[qid] = []
        sdict[qid].append((score_list[index], items[0]))
        index += 1
    lev0, lev1 = float(0), float(0)
    of = open('/QAcorpus/acc.lstm', 'a')
    for qid, cases in sdict.items():
        cases.sort(key=operator.itemgetter(0), reverse=True)
        score, flag = cases[0]
        if flag == '1':
            lev1 += 1
        if flag == '0':
            lev0 += 1
    for s in score_list:
        of.write(str(s) + '\n')
    of.write('lev1:' + str(lev1) + '\n')
    of.write('lev0:' + str(lev0) + '\n')
    print 'lev1:' + str(lev1)
    print 'lev0:' + str(lev0)
    of.close()

if __name__=='__main__':
    pass