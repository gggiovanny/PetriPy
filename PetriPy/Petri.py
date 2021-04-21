import numpy as np

class Node:
    def __init__(self, name_initial, id):
        self.id = id
        self.nextNodes = []
        self.name_initial = name_initial
        if name_initial == 'transition':
            self.listExpectedType = Place
        elif name_initial == 'places':
            self.listExpectedType = Transition
        else:
            raise ValueError('Error!', 'No se configuro un tipo de nodo') 
    def getName(self):
        return "{}{}".format(self.name_initial, self.id)
    def print(self):
        print(self.getName(),'-> ', end='')
    def printNextNames(self):
        for node in self.nextNodes:
            print(node.getName())
    def addNext(self, node):
        if isinstance(node, self.listExpectedType):
            self.nextNodes.append(node)
        else:
            raise ValueError('Error de tipo de datos!', "No se puede agregar un {} a una lista que espera {}".format( node.__class__.__name__, self.listExpectedType.__name__) ) 

class Transition(Node):
    def __init__(self, id):
        Node.__init__(self, 'transition', id)
        self.preconditions = []
        self.wait_time = 15
        self.time_waited = 0
        self.action = self.doNothing # default action
    def runAction(self):
        print("Executing action for:", self.getName())
        self.action()
    def print(self, end_of_line = ''):
        print("{}[{}]".format(self.getName(), self.time_waited),'-> ', end=end_of_line)
    def doNothing(self):
        pass

class Place(Node):
    def __init__(self, id):
        Node.__init__(self, 'places', id)
        self.marks = 0
        self.required_marks = 1
    def print(self):
        print("{}[{}]".format(self.getName(), self.marks),'-> ', end='')

class Network:
    def __init__(self, places_list, transitions_list, initial_state_list = [], max_width = False, name = "", active = False):
        self.places = places_list
        self.transitions = transitions_list
        self.configurePreconditions()
        self.setInitialState(initial_state_list)
        self.global_time = 0
        self.max_width = max_width # "ancho" de la red. Se refiere a el numero de elementos (lugares y transiciones) unicos que se pueden recorrer antes de repetirse
        self.name = name
        self.active = active
    def setInitialState(self, initial_state_list):
        if initial_state_list:
            if len(initial_state_list) == len(self.places):
                for i in range(len(self.places)):
                    self.places[i].marks = initial_state_list[i]
            else:
                raise ValueError('Error!', 'Error en el numero de elementos en initial_state_list: se esperaban {} elementos y se recibieron {}.'.format(len(self.places), len(initial_state_list))) 
    def configurePreconditions(self):
        for transition in self.transitions:
            for place in self.places:
                if transition in place.nextNodes:
                    transition.preconditions.append(place)
    def nextStep(self, actual_time = 0):
        if actual_time:
            self.global_time = actual_time
        self.global_time += 1
        for transition in self.transitions: #? Por cada transicion ...
            all_conditions_marked = True
            #? ... validando que se cumplan todas las precondiciones ...
            if transition.time_waited == 0: #? ... solo si no se esta en estado de espera de una transicion que ya cumplió sus precondiciones previamente
                #? Recorriendo todos Place para verficar que se cumplan las marcas (se puede hacer esto porque python asigna objetos por referencia)
                for precondition in transition.preconditions:
                    if precondition.marks < precondition.required_marks:
                        all_conditions_marked = False #! TODO: hacer que se puedan configurar multiples marcas
            if all_conditions_marked: #? Cuando se cumplen todas las condiciones para la transicion...
                if transition.time_waited == transition.wait_time: #? ... ver que se halla esperado el tiempo de espera de la transicion
                    print("(t={}, w={}) ".format(self.global_time, transition.time_waited), end='')
                    transition.runAction()
                    transition.time_waited = 0
                    #? Quitando las marcas de las precondiciones
                    for pre in transition.preconditions:
                        pre.marks = 0
                    #? y poniendoselas a los Place() siguientes
                    for pos in transition.nextNodes:
                        pos.marks += 1
                else:
                    transition.time_waited += 1
    def fastForward(self, number_of_steps):
        for _ in range(number_of_steps):
            self.nextStep()

    def print(self, firstElements = True):
        pointer = self.places[0]
        for _ in range(self.max_width if self.max_width else len(self.places) + len(self.transitions)):
            pointer.print()
            if firstElements:
                pointer = pointer.nextNodes[0]
            else:
                pointer = pointer.nextNodes[-1]
        print()
    def getMatrixPre(self, show=False, log=False):
        # Generando la matriz PRE (condiciones que tiene que cumplir cada transicion para efectuarse)
        # Debe quedar con las transiciones en el eje horizontal y los lugares en el eje vertical:
        #   t0 t1 t2
        # p0 1  0  0 
        # p1 0  1  0 
        # p2 1  0  1 
        # De momento se genera con los ejes inversos y recorre diferente al imprimirlo en pantalla
        pre = []
        for transition in self.transitions:
            pre_col = []
            for place in self.places:
                if transition in place.nextNodes:
                    pre_col.append(1)
                else:
                    pre_col.append(0)
            pre.append(pre_col)
            
        pre_np = np.asarray(pre).transpose()
        if log: np.savetxt("./logs/pre.csv", pre_np, delimiter=',')
        
        if show:
            print("PRE MATRIX:")
            for i in range(len(pre[0])):
                for j in range(len(pre)):
                    print(pre[j][i], end=' ')
                print()
    def getMatrixPos(self, show=False, log=False):
        # Generando la matriz POS (condiciones que se cumplen luego de una transicion)
        pos = []
        for transition in self.transitions:
            pos_col = []
            for place in self.places:
                if place in transition.nextNodes:
                    pos_col.append(1)
                else:
                    pos_col.append(0)
            pos.append(pos_col)
            
        pos_np = np.asarray(pos).transpose()
        if log: np.savetxt("./logs/pre.csv", pos_np, delimiter=',')
            
        if show:
            print("POS MATRIX:")
            for i in range(len(pos[0])):
                for j in range(len(pos)):
                    print(pos[j][i], end=' ')
                print()
        return pos_np

#? Regresa una lista de objetos Places() que tienen como ID el rango de numeros pasado como argumento
def generatePlaces(range_of_ids):
    _p = []
    for i in range_of_ids:
        _p.append(Place(i)) # se le pasa i como argumento, que sera la id del Place()
    return _p

#? Regresa una lista de objetos Transition() que tienen como ID el rango de numeros pasado como argumento
def generateTransitions(range_of_ids):
    _t = []
    for i in range_of_ids:
        _t.append(Transition(i)) # se le pasa i como argumento, que sera la id del Transition()
    return _t

#? Red para pruebas
def getDemoNetwork():
    # Generando una lista de objetos Places() (Lugares) en una lista llamada 'places'
    places = generatePlaces(range(6))
    # Repitiendo el mismo proceso para generar los objetos tipo Transition() en la lista 'transition'
    transition = generateTransitions(range(5))
    # Estableciendo las relaciones entre Places y Transitions
    places[0].addNext(transition[0]) 
    transition[0].addNext(places[1])
    places[1].addNext(transition[1])
    transition[1].addNext(places[2])
    places[2].addNext(transition[2])
    transition[2].addNext(places[0])
    #
    places[3].addNext(transition[0])
    transition[0].addNext(places[4])
    places[4].addNext(transition[3])
    transition[3].addNext(places[5])
    places[5].addNext(transition[4])
    transition[4].addNext(places[3])
    #
    initial_state = [1,0,0,1,0,0]
    return Network(places, transition, initial_state, 6)

if __name__ == "__main__":
    Petri = getDemoNetwork()
    Petri.getMatrixPre(show=True)
    Petri.getMatrixPos(show=True)
    print("Acciones de las transiciones:")
    Petri.fastForward(60)
    print()
    print("Estado final de la red:")
    Petri.print()
    print()