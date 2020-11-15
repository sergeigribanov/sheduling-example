import json
from ortools.sat.python import cp_model

wdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
dshifts = ['day', 'night']

def main():
    with open('shift_input.json', 'r') as ifl:
        data = json.load(ifl)
        
    model = cp_model.CpModel()
    shifts = {}
    name_fcn = lambda entry: '{first name}_{last name}'.format(**entry)
    for shifter in data['shifters']:
        name = name_fcn(shifter)
        for day in range(data['num days']):
            for shift in range(data['num shifts']):
                key = name, day, shift
                shifts[key] = model.NewBoolVar('shift_{}_{}_{}'.format(*key))

    for day in range(data['num days']):
        for shift in range(data['num shifts']):
            model.Add(sum(shifts[(name_fcn(s), day, shift)] for s in data['shifters']) == 2)

    x = 0
    for shifter in data['shifters']:
        name = name_fcn(shifter)
        n = data['first day']
        nshifts = 0
        prev = 0;
        for day in range(data['num days']):
            tmp = sum(shifts[(name, day, shift)] for shift in range(data['num shifts']))
            model.Add(tmp + prev <= 1)
            prev = tmp
            prefs = shifter['preferences'][wdays[n % 7]] 
            for shift in range(data['num shifts']):
                key = (name_fcn(shifter), day, shift)
                nshifts += shifts[key]
                if prefs[shift] == -1:
                    model.Add(shifts[key] == 0)
                else:
                    x += prefs[shift] * shifts[key]

            n += 1
            
        model.Add(nshifts >= data['num days'] // 7)
        model.Add(nshifts <= 2 * data['num days'] // 7)
        
        
    model.Maximize(x)

    solver = cp_model.CpSolver()
    solver.Solve(model)

    n = data['first day']
    for day in range(data['num days']):
        print('\nday : {}, {}'.format(day, wdays[n % 7]))
        for shifter in data['shifters']:
            name = name_fcn(shifter)
            for shift in range(data['num shifts']):
                if solver.Value(shifts[(name, day, shift)]) == 1:
                    print('{} : {}'.format(name, dshifts[shift]))
        n += 1

if __name__ == '__main__':
    main()
