import os

parmela = 'wine ~/.wine/drive_c/LANL/parmela.exe '


def getvar(filename):
    file = open(filename, 'rb')
    lines = file.readlines()
    file.close()
    mark = []
    step = []
    left_range = []
    right_range = []
    for line in lines:
        line = line.strip()
        var = line.split()
        if var != []:
            if (var[0] == '!@var' and var[1] == '1'):
                mark.append(var[2])
                step.append(var[3])
                left_range.append(var[4])
                right_range.append(var[5])
    return mark, step, left_range, right_range


def rewriteFile(filename, mark, value):
    file = open(filename, 'rU')
    lines = file.readlines()
    file.close()
    k = 0
    for line in lines:
        line = line.strip()
        subs = line.split()
        if subs != []:
            if (subs[0] == '!@subs'):
                ln = len(subs)
                if(ln >= 4 and subs[3] == mark):
                    for i in range(int(subs[1])):
                        new_line = lines[k + i + 1]
                        new_line = new_line.split(' ')
                        new_line[int(subs[2])] = value
                        new_line = ' '.join(new_line)
                        lines[k + i + 1] = new_line
                if(ln >= 6 and subs[5] == mark):
                    for i in range(int(subs[1])):
                        new_line = lines[k + i + 1]
                        new_line = new_line.split(' ')
                        new_line[int(subs[4])] = value
                        new_line = ' '.join(new_line)
                        lines[k + i + 1] = new_line
        k += 1
    file = open(filename, 'w')
    file.writelines(lines)
    file.close()


def analyzeResult(filename, pos):
    IsOk = 0
    goodpos = 0
    file = open(filename, 'rU')
    lines = file.readlines()
    file.close()
    element = []
    number = []
    for i in range(1, pos):
        element.append(str(i))
    for i in range(10000, 20001):
        number.append(str(i))
    for line in lines:
        line = line.strip()
        words = line.split()
        if words != []:
            if (words[0] in element and words[1] in number):
                if words[1] == '20000':
                    IsOk = 1
                    goodpos = words[0]
                else:
                    IsOk = 0
    return IsOk, goodpos


def main():
    inputfilename = 'scan.acc'
    outfilename = 'OUTPAR.TXT'
    foldername = 'scan_result'
    position = 138
    mark, step, left_range, right_range = getvar(inputfilename)
    if mark == []:
        print('No change of the inputfile, please check the parameter')
    else:
        i = 0
        N = (float(right_range[i]) - float(left_range[i])) / float(step[i])
        N = int(N)
        for j in range(N):
            mk = mark[i]
            value = str(float(left_range[i]) + j * float(step[i]))
            rewriteFile(inputfilename, mk, value)
            os.system(parmela + inputfilename)
            IsOk, goodpos = analyzeResult(outfilename, position)
            name = '_' + str(mk) + '_' + str(value)
            os.system('mv EMITTANCE.TBL EMITTANCE_' + str(name) + '.TBL')
            os.system('mv OUTPAR.TXT OUTPAR_' + str(name) + '.TXT')
            print(value, goodpos)
            if IsOk == 1:
                break

        os.system('mv EMITTANCE*.TBL ' + foldername)
        os.system('mv OUTPAR*.TXT ' + foldername)
        os.system('cp ' + inputfilename + ' ' + foldername)
        print('done')


if __name__ == '__main__':
    main()
