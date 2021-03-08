import math
import os
import random, itertools
import xml.etree.ElementTree as et
from xml.dom import minidom

import operator as op
from functools import reduce


def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer // denom


class RandomNDCOP:
    def __init__(self, num_func, min_arity, max_arity, min_tightness, max_tightness, min_domain, max_domain, min_cost, max_cost):
        self.num_func = num_func
        self.min_arity = min_arity
        self.max_arity = max_arity
        self.min_tightness = min_tightness
        self.max_tightness = max_tightness
        self.min_domain = min_domain
        self.max_domain = max_domain
        self.min_cost = min_cost
        self.max_cost = max_cost

    def generate(self, directory, file_name):
        func_arity = [random.randint(self.min_arity, self.max_arity) for _ in range(self.num_func)]
        tightness = random.random() * (self.max_tightness - self.min_tightness) + self.min_tightness
        num_var = 1
        while self._min_comb(num_var) < self.num_func:
            num_var *= 2
        hi = num_var
        lo = int(num_var / 2)
        while lo <= hi:
            mid = int((lo + hi) / 2)
            if self._min_comb(mid) >= self.num_func:
                num_var = mid
                if self._min_comb(mid) == self.num_func:
                    break
                hi = mid - 1
            else:
                lo = mid + 1
        num_var = int(max(num_var, (1 - tightness) * sum(func_arity) + 1))
        domains = [random.randint(self.min_domain, self.max_domain) for _ in range(num_var)]
        root = et.Element('instance')
        et.SubElement(root, 'presentation', {'type': 'NDCOP', 'continuous': 'true'})
        agents = et.SubElement(root, 'agents', {'nbAgents': str(num_var)})
        for i in range(num_var):
            a_id = i + 1
            et.SubElement(agents, 'agent', {'name': 'A{}'.format(a_id), 'id': str(a_id)})
        unique_domain = set(domains)
        unique_domain = list(unique_domain)
        domains_label = et.SubElement(root, 'domains', {'nbDomains': str(len(unique_domain))})
        domain_info = dict()
        for i in range(len(unique_domain)):
            d_id = i + 1
            et.SubElement(domains_label, 'domain', {'name': 'D{}'.format(d_id), 'nbValues': str(unique_domain[i])})
            domain_info[unique_domain[i]] = 'D{}'.format(d_id)
        variables = et.SubElement(root, 'variables', {'nbVariables': str(num_var)})
        for i in range(num_var):
            a_id = i + 1
            domain = domains[i]
            et.SubElement(variables, 'variable',
                          {'agent': 'A{}'.format(a_id), 'name': 'X' + str(a_id) + '.1', 'domain': domain_info[domain]})
        constraints = et.SubElement(root, 'constraints', {'nbConstraints': str(self.num_func)})
        relations = et.SubElement(root, 'relations', {'nbRelations': str(self.num_func)})
        rel_domains = []
        for i in range(self.num_func):
            c_id = i + 1
            arity = random.randint(self.min_arity, self.max_arity)
            involoved_vars = random.sample(range(num_var), arity)
            scope = ['X{}.1'.format(j + 1) for j in involoved_vars]
            et.SubElement(constraints, 'constraint',
                          {'name': 'C{}'.format(c_id), 'arity': str(arity), 'scope': ' '.join(scope), 'reference': 'R{}'.format(c_id)})
            et.SubElement(relations, 'relation', {'name': 'R{}'.format(c_id), 'arity': str(arity)})
            rel_domains.append([[j for j in range(domains[k])] for k in involoved_vars])
        xmlstr = minidom.parseString(et.tostring(root)).toprettyxml(indent="   ")
        relation_folder = os.path.join(directory, 'relations')
        if not os.path.exists(relation_folder):
            os.makedirs(relation_folder)
        with open(os.path.join(directory, file_name), "w") as f:
            f.write(xmlstr)
        relation_folder = os.path.join(relation_folder, file_name[: -4])
        os.mkdir(relation_folder)
        idx = 1
        for doms in rel_domains:
            f = open(os.path.join(relation_folder, 'R{}'.format(idx)), 'w')
            idx += 1
            total = 1
            for dd in doms:
                total *= len(dd)
            i = 1
            for _ in itertools.product(*doms):
                util = random.random() * (self.max_cost - self.min_cost) + self.min_cost
                f.write('{0:.6f}'.format(util))
                if i % 1000 == 0:
                    f.write('\n')
                elif i != total:
                    f.write('|')
                i += 1
            f.close()

    def _min_comb(self, num_var):
        if num_var < self.max_arity:
            return -1
        combs = [ncr(num_var, i) for i in range(self.min_arity, self.max_arity + 1)]
        return min(combs)