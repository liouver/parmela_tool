'''parmela tool, used to optimize the beamline.
scan the value to meak all the electron pass the beamline
Created by W.Liu @ Dec, 2017
'''
import os

parmela = 'wine ~/.wine/drive_c/LANL/parmela.exe '
inputfilename = 'scan.acc'
parmeterfilename = 'EMITTANCE.TBL'
outfilename = 'OUTPAR.TXT'
foldername = 'opt_result'
last_element = 142


def getvar(filename):
    file = open(filename, 'rU')
    lines = file.readlines()
    file.close()
    mark = []
    tempmark = []
    step = []
    tempstep = []
    left_range = []
    templeft_range = []
    right_range = []
    tempright_range = []
    pos = []
    for line in lines:
        line = line.strip()
        var = line.split()
        ln = len(var)
# when open file with 'rU' doesn't work (ASCII decode doesn't work)
# change 'rU' to 'rb' and use following loop to see which word can't decode
#        for i in range(ln):
#            print(var[i])
#            var[i] = var[i].decode('ASCII')
        if var != []:
            if (var[0] == '!@var' and var[1] == '1'):
                tempmark.append(var[2])
                tempstep.append(var[3])
                templeft_range.append(var[4])
                tempright_range.append(var[5])
            if (var[0] == '!@subs'):
                if(ln >= 4 and var[3] in tempmark):
                    mark.append(var[3])
                    if(ln >= 6 and var[-2] == 'element'):
                        pos.append(int(var[-1]))
                if(ln >= 6 and var[5] in tempmark):
                    mark.append(var[5])
                    if(ln >= 8 and var[-2] == 'element'):
                        pos.append(int(var[-1]))
    ln1 = len(mark)
    ln2 = len(tempmark)
    for i in range(ln1):
        for j in range(ln2):
            if tempmark[j] == mark[i]:
                step.append(tempstep[j])
                left_range.append(templeft_range[j])
                right_range.append(tempright_range[j])
    return mark, step, left_range, right_range, pos


def rewriteFile(filename, mark, step):
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
                        new_line = new_line.split()
                        value = float(new_line[int(subs[2])]) + step
                        new_line[int(subs[2])] = str(value)
                        new_line = ' '.join(new_line) + '\n'
                        lines[k + i + 1] = new_line
                if(ln >= 6 and subs[5] == mark):
                    for i in range(int(subs[1])):
                        new_line = lines[k + i + 1]
                        new_line = new_line.split()
                        value = float(new_line[int(subs[2])]) + step
                        new_line[int(subs[2])] = str(value)
                        new_line = ' '.join(new_line) + '\n'
                        lines[k + i + 1] = new_line
                if(ln >= 4 and subs[3] == ('-' + mark)):
                    new_line = lines[k + i + 1]
                    new_line = new_line.split()
                    value = -1 * (float(new_line[int(subs[2])]) + step)
                    new_line[int(subs[2])] = str(value)
                    new_line = ' '.join(new_line) + '\n'
                    lines[k + i + 1] = new_line
                if(ln >= 6 and subs[5] == ('-' + mark)):
                    new_line = lines[k + i + 1]
                    new_line = new_line.split()
                    value = -1 * (float(new_line[int(subs[2])]) + step)
                    new_line[int(subs[2])] = str(value)
                    new_line = ' '.join(new_line) + '\n'
                    lines[k + i + 1] = new_line
                print('mark:', mark, 'value:', str(value))
        k += 1
    file = open(filename, 'w')
    file.writelines(lines)
    file.close()


def get_results(filename):
    file = open(filename, 'rU')
    lines = file.readlines()
    file.close()
    line = lines[-1]
    line = line.strip()
    words = line.split()
    z_pos = words[1]
    beamsize = (words[8] + words[9]) / 2
    emittance = (words[5] + words[6]) / 2
    energy = words[11]
    return z_pos, beamsize, emittance, energy


def judge_result(filename):
    IsOk = 0
    goodpos = 0
    file = open(filename, 'rU')
    lines = file.readlines()
    file.close()
    element = []
    number = []
    for i in range(1, last_element + 1):
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
                    break
    return IsOk, goodpos


def optimize_system():
    mark, step, left_range, right_range, pos = getvar(inputfilename)
    if mark == []:
        print('No change of the inputfile, please check the parameter')
    else:
        os.system(parmela + inputfilename)
        IsOk, goodpos = judge_result(outfilename)
        if IsOk == 0:
            print('Electrons loss in the beamline, please make sure all the \
                  electrons pass the beamline before use this code')
        elif IsOk == 1:
            opt_value = get_results(parmeterfilename)
            min_value = opt_value[1]
            last_value = min_value
            ln_mark = len(mark)
            last_error = 1
            k = 0
            while last_error > 0:
                for i in range(ln_mark):
                    print(mark[i], step[i], left_range[i], right_range[i])
                    mk = mark[i]
                    step_value = float(step[i])
                    rewriteFile(inputfilename, mk, step_value)
                    os.system(parmela + inputfilename)
                    IsOk, goodpos = judge_result(outfilename)
                    if IsOk == 0:
                        print('not pass')
                        step_value = -2 * float(step[i])
                        rewriteFile(inputfilename, mk, step_value)
                        os.system(parmela + inputfilename)
                        IsOk, goodpos = judge_result(outfilename)
                        if IsOk == 0:
                            print('not pass')
                            step_value = float(step[i])
                            rewriteFile(inputfilename, mk, step_value)
                        elif IsOk == 1:
                            opt_value = get_results(parmeterfilename)
                            error = opt_value[1] - min_value
                            if error <= 0:
                                min_value = opt_value[1]
                            elif error > 0:
                                step_value = float(step[i])
                                rewriteFile(inputfilename, mk, step_value)
                            print(opt_value[1])
                    elif IsOk == 1:
                        opt_value = get_results(parmeterfilename)
                        error = opt_value[1] - min_value
                        if error <= 0:
                            min_value = opt_value[1]
                            print(min_value)
                        elif error > 0:
                            step_value = -2 * float(step[i])
                            rewriteFile(inputfilename, mk, step_value)
                            os.system(parmela + inputfilename)
                            IsOk, goodpos = judge_result(outfilename)
                            if IsOk == 0:
                                print('not pass')
                                step_value = float(step[i])
                                rewriteFile(inputfilename, mk, step_value)
                            elif IsOk == 1:
                                opt_value = get_results(outfilename)
                                error = opt_value[1] - min_value
                                if error <= 0:
                                    min_value = opt_value[1]
                                elif error > 0:
                                    step_value = float(step[i])
                                    rewriteFile(inputfilename, mk, step_value)
                                print(opt_value[1])
                last_error = last_value - min_value
                last_value = min_value
                k += 1
                print('loop:', k, 'min value:', min_value)
                if k >= 10:
                    break


def main():
    optimize_system()
    os.system('cp ' + inputfilename + ' ' + foldername)
    print('done')


if __name__ == '__main__':
    main()
