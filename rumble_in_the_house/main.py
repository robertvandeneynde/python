#!/usr/bin/python2

import pygame
import random
import colors

pygame.init()

WINDOW_SIZE = (1024,768)
FPS = 50

from mymath import Vec

class PixelCollisionManager(object):
    def __init__(self, json, dirname):
        import os
        assert json['type'] == "pixelmap"
        self.pixsource = pygame.image.load(os.path.join(dirname, json['source']))
        
        self.aliases = list(map(str,json['aliases'])) # unicode -> str
        
        y_special = self.pixsource.get_height() - 1
        self.colormap = dict(
            (
                tuple( self.pixsource.get_at((i, y_special)) ),
                alias
            )
            for i,alias in enumerate(self.aliases)
        )
        
        self.groups = dict(
            (
                str(name),
                str(reg)
            )
            for name,reg in json.setdefault("groups",{}).items()
        )
            
    def size_match_image(self, image):
        pixw,pixh = self.pixsource.get_size()
        dispw,disph = image.get_size()
        return pixw == dispw and pixh == disph + 1
            
    def get_aliases(self):
        return self.aliases
    
    def get_groups(self):
        return self.groups
    
    def point_match_group(self, point, groupname):
        alias = self.get_alias(point)
        if alias is None:
            return False
        return re.match(self.groups[groupname], alias)
    
    def get_alias(self, point):
        try:
            color = self.pixsource.get_at( Vec(point) - (0,1) )
        except IndexError:
            return None
        try:
            return self.colormap[ tuple(color) ]
        except KeyError:
            return None
        
class ImageDisplay(object):
    def __init__(self, image):
        self.image = image
        self._collision = None
    
    def get_collision(self):
        return self._collision
    
    def set_collision(self, collision):
        assert collision.size_match_image(self.image)
        self._collision = collision
        
    collision = property(get_collision, set_collision)
        
class ImagePixelCollision(object):
    
    def __init__(self, filename):
        import json
        tree = json.load(open(filename))
        import os
        dirname = os.path.dirname(filename)
        self.displays = dict(
            (
                str(alias),
                ImageDisplay( pygame.image.load(os.path.join(dirname, filename) ) )
            )
            for alias,filename in tree['displays'].items()
        )
        
        self.collisions = dict(
            (
                str(alias),
                PixelCollisionManager(json, dirname)
            )
            for alias,json in tree['collisions'].items()
        )
        
        import re
        
        self.displaycollision = dict()
        for reg_disp,the_coll in tree['displaycollision']:
            reg_disp,the_coll = map(str, (reg_disp,the_coll))
            
            for name,disp in self.displays.items():
                obj = re.match(reg_disp, name)
                if obj:
                    coll_name = the_coll.format(*obj.groups())
                    disp.collision = self.collisions[coll_name]
            
        
    def get_display(self, name):
        return self.displays[name]
        
class GraphicalPerso(object):
    imagecollision = ImagePixelCollision("res/pion.img")
    state = imagecollision.get_display('normal')
    image = state.image
    collision = state.collision
    
    def __init__(self, name):
        self.name = name
        self.salle = None
        self.position = (0,0)
        self.joueur = None
        self.points = None
        
        self.state = self.imagecollision.get_display('normal')
        
    def __repr__(self):
        return self.name
    
    def set_joueur(self, joueur):
        if self.joueur:
            self.joueur.persos.remove(self)
        self.joueur = joueur
        if self.joueur:
            self.joueur.persos.add(self)
        
    def move_to(self, destination):
        self.salle.move_perso(self, destination)
    
    @property
    def rect(self):
        return self.image.get_rect(center=self.position)
    
    @property
    def image(self):
        return self.state.image
        
    @property
    def collision(self):
        return self.state.collision
    
    def change_display(self, new_name):
        self.state = self.imagecollision.get_display(new_name)
    
    def general_collide(self, point):
        return self._get_collision_alias(point) is not None

    def _get_collision_alias(self,point):
        relpoint = Vec(point) - self.rect.topleft
        return self.collision.get_alias(relpoint)

from mymath import Vec

class Node(object):
    imagecollision = ImagePixelCollision("res/salle.img")
    font = pygame.font.SysFont("Times",16)
    
    def __init__(self, position=(0,0)):
        self.destinations = set()
        self.persos = set()
        
        self.position = position
        self.state = self.imagecollision.get_display("rollover")
        
    def __repr__(self):
        return repr(self.position)
    
    @property
    def rect(self):
        return self.image.get_rect(center=self.position)
    
    @property
    def image(self):
        return self.state.image
        
    @property
    def collision(self):
        return self.state.collision
    
    def change_display(self, new_name):
        self.state = self.imagecollision.get_display(new_name)
        
    def add_perso(self, perso):
        self.persos.add(perso)
        perso.salle = self
        
    def delete_perso(self, perso):
        self.persos.remove(perso)
        perso.salle = None
    
    def move_perso(self, perso, destination):
        if destination not in self.destinations:
            raise ValueError("in move_perso the destination must be in destinations")
        self.delete_perso(perso)
        destination.add_perso(perso)
    
    def make_liaison(self,other):
        if self is other:
            return # Can't make liaison from self to self
        self.destinations.add(other)
        other.destinations.add(self)
    
    def remove_liaison(self,other):
        self.destinations.remove(other)
        other.destinations.remove(self)
    
    def adjust_position(self, tolerance=20):
        x,y = self.position
        xchoices,ychoices = [],[]
        
        for sx,sy in (node.position for node in self.destinations):
            dx = abs(sx - x)
            if dx <= tolerance:
                xchoices.append( (dx,sx) )
            dy = abs(sy - y)
            if dy <= tolerance:
                ychoices.append( (dy,sy) )
        
        if len(xchoices):
            x = min(xchoices)[1]
        if len(ychoices):
            y = min(ychoices)[1]
        
        self.position = (x,y)
    
    def general_collide(self, point):
        alias = self._get_collision_alias(point)
        return alias is not None
    
    def grab_collide(self,point):
        return self._get_collision_alias(point) == "grab"
    
    def connection_collide(self,point):
        return self._get_collision_alias(point) in ("normal","connect")
    
    def _get_collision_alias(self,point):
        relpoint = Vec(point) - self.rect.topleft
        return self.collision.get_alias(relpoint)
    
    def _update_perso_positions(self):
        positions = [
            self.position + Vec(p) * (self.rect.width / 4)
            for p in [(0,0),(-1,-1),(+1,+1),(+1,-1),(-1,+1),
                      (0,-1),(+1,0),(0,+1),(-1,0)]
        ]
        for i,p in enumerate(self.persos):
            p.position = positions[i]

NAMES = list(map(chr,range(ord('A'), ord('Z') + 1)))

from collections import namedtuple
from mymath import Vec

class Player:
    def __init__(self, name):
        self.persos = set()
        self.name = name
        self.points = 0
    
    def add_perso(self, perso):
        if perso.joueur != self:
            perso.set_joueur(self)
            
    def clear_persos(self):
        for perso in list(self.persos): #copy
            perso.set_joueur(None)

class Terrain:
    """ Model """
    def __init__(self, maximum_salles=12):
        self.maximum_salles = 12
        self.salles = []
        
    def add_salle(self, salle):
        self.salles.append(salle)
    
    def correct(self):
        return (
                len(self.salles) == self.maximum_salles
            and self._nodes_connected()
        )
        
    def _nodes_connected(self):
        non_accessibles = set(self.salles)
        deja_traites = set()
        def f(s):
            non_accessibles.discard(s)
            deja_traites.add(s)
            for d in s.destinations:
                if d not in deja_traites:
                    f(d)
        f( next(iter(non_accessibles)) )
        return len(non_accessibles) == 0

class Round:
    """Low Level Controller"""
    def __init__(self, partie):
        self.partie = partie
        self.joueurs = partie.joueurs
        self.persos = self.partie.persos
        self.finished = False
        
        self.persos_vivants = set(self.persos)
        self.persos_morts = []
        
        for p in self.persos:
            p.points = None
        
        for joueur in self.joueurs:
            joueur.clear_persos()
        
        random_persos = list(self.persos)
        random.shuffle(random_persos)
        it = iter(random_persos)
        for joueur in self.joueurs:
            for i in range(2):
                joueur.add_perso( next(it) )
        
        min_points = min(j.points for j in self.joueurs)
        self.current_player_index = random.choice([
            i for i,j in enumerate(self.joueurs)
            if j.points == min_points
        ])
        
        for salle,perso in zip(self.partie.terrain.salles,self.persos):
            salle.add_perso(perso)
    
    def joueur_actuel(self):
        return self.joueurs[self.current_player_index]
    
    def _next_player(self):
        self.current_player_index += 1
        self.current_player_index %= len(self.joueurs)
        
    def _end_game(self):
        self.kill( next(iter(self.persos_vivants)) )
        for joueur in self.joueurs:
            joueur.points += max(p.points for p in joueur.persos)
            
        self.finished = True
    
    def kill(self, perso):
        self.persos_vivants.remove(perso)
        perso.salle.delete_perso(perso)
        perso.points = max(0, len(self.persos_morts) - 1)
        self.persos_morts.append(perso)
        
        if len(self.persos_vivants) == 1:
            self._end_game()
        else:
            self._next_player()
    
    def move(self, perso, destination):
        perso.move_to(destination)
        self._next_player()
    
    def is_finished(self):
        return self.finished

class Partie:
    """ Low Level Controller """
    def __init__(self, terrain, nombre_joueurs):
        self.terrain = terrain
        
        self.persos = [
            GraphicalPerso(name)
            for name,salle in zip(NAMES,self.terrain.salles)
        ]
            
        self.joueurs = [
            Player("J{}".format(chr(ord('1') + i)))
            for i in range(nombre_joueurs)
        ]
        
        self.rounds = []
    
    def next_round(self):
        self.rounds.append( Round(self) )
        
    def current_round(self):
        return self.rounds[-1]
    
    def is_finished(self):
        return len(self.rounds) == 3 and self.current_round.is_finished()
    
class Main:
    """ View and High Level Controller"""
    
    GrabMode = namedtuple('GrabMode', ['node','grab_point'])
    ConnectionMode = namedtuple('ConnectionNode', ['node'])
    WaitingPlacement = namedtuple('WaitingPlacement', [])
    
    for mode in (GrabMode,ConnectionMode,WaitingPlacement):
        mode.defaultmode = WaitingPlacement
    
    PlayMode = namedtuple('PlayMode', [])
    MovePersoMode = namedtuple('MovePersoMode', ['perso'])
    
    for mode in (MovePersoMode,PlayMode):
        mode.defaultmode = PlayMode
        
    FinRound = namedtuple("FinRound", [])
    FinPartie = namedtuple("FinPartie", [])
    
    for mode in (FinRound,FinPartie):
        mode.defaultmode = mode
    
    def __init__(self):
        self.terrain = Terrain(12)
        self.partie = None
        self.round = None
        
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.mode = self.WaitingPlacement()
        self.finished = False
    
    def try_begin_game(self):
        if self.terrain.correct():
            self.begin_game()
    
    def begin_game(self):
        if self.partie and self.partie.is_finished():
            self.mode = self.FinPartie()
        else:
            self.mode = self.PlayMode()
            if self.partie is None:
                self.partie = Partie(self.terrain, 4)
            self.partie.next_round()
            self.round = self.partie.current_round()
        
    def kill(self, perso):
        self.round.kill(perso)
        if self.round.is_finished():
            self.mode = self.FinRound()
        else:
            self.mode = self.PlayMode()
            
    def move_perso(self, perso, destination):
        self.round.move(perso, destination)
        if self.round.is_finished():
            self.mode = self.FinRound()
        else:
            self.mode = self.PlayMode()
        
    def find_salle_collider(self, point):
        for s in self.terrain.salles:
            if s.general_collide(point):
                return s
        return None
    
    def find_pion_collider(self, point):
        for p in self.partie.persos:
            if p.salle and p.general_collide(point):
                return p
        return None
    
    def draw_connection_line(self, p1, p2):
        for color,width in zip([colors.YELLOW,colors.BROWN],[10,5]):
            pygame.draw.line(self.screen, color, p1, p2, width)
    
    def draw_perso(self, perso):
        rend = Node.font.render(perso.name, True, colors.WHITE)
        fontrect = rend.get_rect(center=perso.position)
        
        image = perso.image
        rect = image.get_rect(center=perso.position)
        self.screen.blit(image, rect)
        self.screen.blit(rend,fontrect)
        
        if perso.points is not None:
            texte = str(perso.points)
            rend = Node.font.render(texte, True, colors.WHITE)
            fontrect = rend.get_rect(center=Vec(perso.position) - (0,30))
            self.screen.blit(rend,fontrect)
    
    def update_morts_persos_position(self):
        for i,perso in enumerate(self.round.persos_morts):
            perso.position = (50 + i * 50, WINDOW_SIZE[1] - 40)
    
    def draw_salle(self, salle):
        salle._update_perso_positions()
        
        self.screen.blit(salle.image, salle.rect)
        
        for i,perso in enumerate(salle.persos):
            self.draw_perso(perso)
    
    def treat_event(self, event):
        mouse_position = pygame.mouse.get_pos()
        
        if event.type == pygame.QUIT: 
            self.finished = True
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            
            if type(self.mode) is self.WaitingPlacement:
                collider = self.find_salle_collider(mouse_position)
                if collider:
                    
                    if collider.grab_collide(mouse_position):
                        self.mode = self.GrabMode(
                            collider,
                            Vec(collider.position) - mouse_position
                        )
                    elif collider.connection_collide(mouse_position):
                        self.mode = self.ConnectionMode(collider)
                    else:
                        self.mode = self.WaitingPlacement()
                    
                else:
                    if len(self.terrain.salles) < self.terrain.maximum_salles:
                        new_node = Node(mouse_position)
                        if len(self.terrain.salles):
                            self.terrain.salles[-1].make_liaison(new_node)
                            
                        self.terrain.add_salle(new_node)
                        self.mode = self.GrabMode(new_node, (0,0))
                    else:
                        self.mode = self.WaitingPlacement()
                        
            elif type(self.mode) is self.PlayMode:
                perso = self.find_pion_collider(mouse_position)
                if perso:
                    salle = perso.salle
                    if len(salle.persos) > 1:
                        self.kill(perso)
                    else:
                        destinations = salle.destinations
                        if len(destinations) == 1:
                            self.move_perso(perso, next(iter(destinations)))
                        else:
                            self.mode = self.MovePersoMode(perso)
            
            elif type(self.mode) is self.MovePersoMode:
                perso = self.mode.perso
                collider = self.find_salle_collider(mouse_position)
                if collider and collider != perso.salle:
                    try:
                        self.move_perso(perso,collider)
                    except ValueError:
                        pass
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            
            if type(self.mode) is self.ConnectionMode:
                node = self.mode.node
                collider = self.find_salle_collider(mouse_position)
                if collider:
                    try:
                        node.remove_liaison(collider)
                    except KeyError:
                        node.make_liaison(collider)
                        
            if self.mode.defaultmode is self.WaitingPlacement:
                self.mode = self.WaitingPlacement()
            
        elif event.type == pygame.KEYDOWN:
            if type(self.mode) in (self.WaitingPlacement, self.FinRound):
                if event.key == pygame.K_p:
                    self.try_begin_game()
    
    def enter_frame(self):  
        mouse_position = pygame.mouse.get_pos()
        
        if type(self.mode) is self.GrabMode:
            node,grab_point = self.mode
            node.position = Vec(mouse_position) + Vec(grab_point)
            node.adjust_position()
            
        elif type(self.mode) in (self.ConnectionMode, self.WaitingPlacement):
            
            for s in self.terrain.salles:
                if s.general_collide(mouse_position):
                    s.change_display("rollover")
                else:
                    s.change_display("normal")
                    
            if type(self.mode) is self.ConnectionMode:
                self.mode.node.change_display("rollover")
        
        elif type(self.mode) is self.PlayMode:
            for s in self.terrain.salles:
                s.change_display('normal')
                for p in s.persos:
                    if p.general_collide(mouse_position):
                        p.change_display("rollover")
                    else:
                        p.change_display("normal")

        elif type(self.mode) is self.MovePersoMode:
            perso = self.mode.perso
            for s in self.terrain.salles:
                if s in perso.salle.destinations:
                    s.change_display('rollover')
                elif s.general_collide(mouse_position):
                    s.change_display('rollover')
                else:
                    s.change_display('normal')
                    
                for p in s.persos:
                    if p is perso:
                        p.change_display("rollover")
                    else:
                        p.change_display("normal")
        
        if type(self.mode) in (self.PlayMode, self.FinRound):
            for p in self.round.persos_morts:
                p.change_display("normal")
                
    def draw(self):
        self.screen.fill(colors.BLACK)
        pygame.draw.rect(self.screen, colors.BROWN, (
            (0, WINDOW_SIZE[1] - 80),
            (WINDOW_SIZE[0], 80)
        ))
        pygame.draw.rect(self.screen, colors.BROWN, (
            (WINDOW_SIZE[0] - 130, 0),
            (130, WINDOW_SIZE[1])
        ))
        
        mouse_position = pygame.mouse.get_pos()
        
        for s in self.terrain.salles:
            for d in s.destinations:
                if id(d) < id(s):
                    self.draw_connection_line(d.position, s.position)
                    
        if type(self.mode) is self.ConnectionMode:
            self.draw_connection_line(self.mode.node.position, mouse_position)
        
        if True:
            for s in self.terrain.salles:
                self.draw_salle(s)
            
        if self.mode.defaultmode is self.PlayMode:
            name = self.round.joueur_actuel().name
            rend = Node.font.render(name, True, colors.BLACK)
            position = Vec(mouse_position) + (0,30)
            fontrect = rend.get_rect(center=position)
            
            for c,w in zip([colors.WHITE, colors.BROWN],[18,15]):
                pygame.draw.circle(self.screen, c, position, w)
            self.screen.blit(rend,fontrect)
        
        if self.mode.defaultmode in (self.PlayMode,self.FinRound):
            self.update_morts_persos_position()
            for p in self.round.persos_morts:
                self.draw_perso(p)
        
        if self.mode.defaultmode in (self.PlayMode,self.FinRound,self.FinPartie):
            for i,joueur in enumerate(self.partie.joueurs):
                text = "({}) {} : {} Point{}".format(
                    ' '.join(map(str,joueur.persos)),
                    joueur.name,
                    joueur.points,
                    "s" if joueur.points != 1 else ""
                )
                rend = Node.font.render(text, True, colors.WHITE)
                fontrect = rend.get_rect(topright=(
                    WINDOW_SIZE[0] - 10,
                    10 + i*60
                ))
                
                self.screen.blit(rend,fontrect)
            
    def run(self):
        self.finished = False
        while not self.finished:
            for event in pygame.event.get():
                self.treat_event(event)
            self.enter_frame()
            self.draw()
            pygame.display.flip()
            self.clock.tick_busy_loop(FPS)
        
        pygame.quit()
        
if __name__ == '__main__':
    Main().run()