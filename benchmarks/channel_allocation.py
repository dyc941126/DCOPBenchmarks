import math
import os
import random
import itertools
import xml.etree.ElementTree as et
from xml.dom import minidom


def distance(loc1, loc2):
    return (loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2


class ChannelAllocation:
    def __init__(self, channel_cnt, num_points, row=100, col=100, p_max=510, p_min=490, bkg_noise=1, w=20):
        self.channel_cnt = channel_cnt
        self.num_points = num_points
        self.row = row
        self.col = col
        self.p_max = p_max
        self.p_min = p_min
        self.bkg_noise = bkg_noise
        self.locations = []
        self.occ_locs = set()
        self.power = []
        self.neighbors = []
        self.constraint_scp = []
        self.utils = []
        self.w = w
        self.avg_arity = 0

    def generate(self):
        for i in range(self.num_points):
            loc = (random.randrange(self.row), random.randrange(self.col))
            while loc in self.occ_locs:
                loc = (random.randrange(self.row), random.randrange(self.col))
            self.locations.append(loc)
            self.occ_locs.add(loc)
            self.power.append(random.random() * (self.p_max - self.p_min) + self.p_min)
        while True:
            single_points = set()
            for i in range(self.num_points):
                neighbors = set()
                for j in range(self.num_points):
                    if i == j or j in single_points:
                        continue
                    if self.power[j] > self.bkg_noise * distance(self.locations[i], self.locations[j]):
                        neighbors.add(j)
                if len(neighbors) == 0 or len(neighbors) > 6:
                    single_points.add(i)
            first_pass = list(single_points)
            for i in range(self.num_points):
                if i in single_points:
                    continue
                neighbors = set()
                for j in range(self.num_points):
                    if i == j or j in single_points:
                        continue
                    if self.power[j] > self.bkg_noise * distance(self.locations[i], self.locations[j]):
                        neighbors.add(j)
                assert len(neighbors) <= 6
                if len(neighbors) == 0:
                    single_points.add(i)
            if len(single_points) == 0:
                break
            for i in single_points:
                self.occ_locs.discard(self.locations[i])
                loc = (random.randrange(self.row), random.randrange(self.col))
                while loc in self.occ_locs:
                    loc = (random.randrange(self.row), random.randrange(self.col))
                self.locations[i] = loc
                self.occ_locs.add(loc)

        for i in range(self.num_points):
            neighbors = set()
            for j in range(self.num_points):
                if i == j:
                    continue
                if self.power[j] > self.bkg_noise * distance(self.locations[i], self.locations[j]):
                    neighbors.add(j)
            assert len(neighbors) > 0
            self.avg_arity += (len(neighbors) + 1)
            self.neighbors.append(neighbors)
        self.avg_arity /= self.num_points
        for i in range(self.num_points):
            loc1 = self.locations[i]
            variables = [i] + sorted(list(self.neighbors[i]))
            self.constraint_scp.append(variables)
            utils = []
            domains = []
            idx = 0
            for j in range(len(variables)):
                domains.append([x for x in range(self.channel_cnt)])
                if variables[j] == i:
                    idx = j
            for item in itertools.product(*domains):
                val = item[idx]
                conf = 0
                for j in range(len(variables)):
                    if j != idx:
                        if abs(val - item[j]) <= 3:
                            loc2 = self.locations[variables[j]]
                            power = self.power[variables[j]]
                            conf += power / distance(loc1, loc2)
                if conf == 0:
                    conf = 1
                u = self.w * math.log2(1 + self.power[i] / conf)
                pref = random.random()
                utils.append(pref + u)
            self.utils.append(utils)

    def save(self, path):
        meta_data = {'type': 'NDCOP', 'avgArity': str(self.avg_arity)}
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if os.path.exists(path):
            os.remove(path)
        root = et.Element('instance')
        et.SubElement(root, 'presentation', meta_data)
        agents = et.SubElement(root, 'agents', {'nbAgents': str(len(self.locations))})
        for agent_id in range(len(self.locations)):
            et.SubElement(agents, 'agent', {'name': 'A{}'.format(agent_id), 'id': str(agent_id),
                                            'description': self.locations[agent_id]})
        domains = et.SubElement(root, 'domains', {'nbDomains': '1'})
        et.SubElement(domains, 'domain', {'name': 'D1', 'nbValues': str(self.channel_cnt)})
        variables = et.SubElement(root, 'variables', {'nbVariables': str(len(self.locations))})
        for agent_id in range(len(self.locations)):
            et.SubElement(variables, 'variable', {'agent': 'A{}'.format(agent_id), 'name': 'X{}.1'.format(agent_id),
                                                  'domain': 'D1',
                                                  'description': 'Variable X{}.1'.format(agent_id)})

        constraints = et.SubElement(root, 'constraints', {'nbConstraints': str(len(self.constraint_scp))})
        scp_idx = 1
        for scp in self.constraint_scp:
            scope_variables = ['X{}.1'.format(x) for x in scp]
            scope = ' '.join(scope_variables)
            arity = str(len(scp))
            et.SubElement(constraints, 'constraint', {'name': 'C{}'.format(scp_idx), 'arity': arity, 'scope': scope,
                                                      'reference': 'R{}'.format(scp_idx)})
            scp_idx += 1

        relations = et.SubElement(root, 'relations', {'nbRelations': str(len(self.constraint_scp))})
        scp_idx = 1
        for util in self.utils:
            name = 'R{}'.format(scp_idx)
            e = et.SubElement(relations, 'relation', {'name': name})
            relation_pth = os.path.join(os.path.dirname(path), 'relations', os.path.basename(path)[: -4])
            if not os.path.exists(relation_pth):
                os.makedirs(relation_pth)
            relation_pth = os.path.join(relation_pth, name)
            f = open(relation_pth, 'w')
            data = []
            for d in util:
                data.append('{0:.6f}'.format(d))
                if len(data) == 1000:
                    f.write('|'.join(data) + '\n')
                    data = []
            if len(data) != 0:
                f.write('|'.join(data) + '\n')
            f.close()
            scp_idx += 1
        xmlstr = minidom.parseString(et.tostring(root)).toprettyxml(indent="   ")
        with open(path, "w") as f:
            f.write(xmlstr)