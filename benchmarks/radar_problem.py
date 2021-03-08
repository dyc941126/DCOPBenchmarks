import math, os
import random
import itertools
import xml.etree.ElementTree as et
from xml.dom import minidom


class Tensor:
    def __init__(self, domains, init_val=0, data=None):
        self.dims = tuple([x for x in domains.keys()])
        self.domains = domains
        self.weights = dict()
        weight = 1
        for x in reversed(list(self.dims)):
            self.weights[x] = weight
            weight *= self.domains[x]
        if data:
            assert len(data) == weight
            self.data = data
        else:
            self.data = [init_val] * weight

    def __len__(self):
        return len(self.data)

    def _get_idx(self, assignment):
        idx = 0
        for x in self.dims:
            idx += assignment[x] * self.weights[x]
        return idx

    def set_value(self, assignment, val):
        self.data[self._get_idx(assignment)] = val

    def get_value(self, assignment):
        return self.data[self._get_idx(assignment)]


def radar_problem(num_rows, num_cols, num_type_1, num_type_2, directory, file_name,
                  radius_min=.05, radius_max=.25, beta=.5):
    radars = dict()
    radars_info = dict()
    universal_domain = ['E', 'N', 'W', 'S', 'EN', 'EW', 'ES', 'NW', 'NS', 'WS', 'ENW', 'ENS', 'EWS', 'NWS', 'ENWS']
    idx = 1
    for row in range(num_rows):
        for col in range(num_cols):
            radars[(col, row)] = 'A' +str(idx)
            radars_info[(col, row)] = []
            idx += 1
    phenomena = dict()
    idx = 1
    radar_radius = 1
    angles = dict()
    for i in range(num_type_1 + num_type_2):
        name = 'P' + str(idx)
        while True:
            x = random.uniform(-1, num_cols)
            y = random.uniform(-1, num_rows)
            ra = []
            radius = random.uniform(radius_min, radius_max)
            for r_x, r_y in radars.keys():
                if distance(x, y, r_x, r_y) <= radar_radius:
                    ra.append((r_x, r_y))
            if 1 < len(ra):
                break
        for r_x, r_y in ra:
            radars_info[(r_x, r_y)].append(name)
        t = 1 if idx <= num_type_1 else 2
        phenomena[name] = ((x, y), t, radius, ra)
        idx += 1
    radars_domain = dict()
    for loc in radars:
        related_phenomena = radars_info[loc]
        if len(related_phenomena) == 0:
            return False
        angles[loc] = dict()
        possible_directions = set()
        for p in related_phenomena:
            (x, y), _, radius, _ = phenomena[p]
            d = distance(x, y, *loc)
            if d < radius:
                angles[loc][p] = {'angle': math.pi * 2, 'start_angle': 0, 'end_angle': math.pi * 2}
                possible_directions.update({'E', 'N', 'W', 'S'})
                continue
            angle = math.asin(radius / d)
            delta_x = x - loc[0]
            a = math.acos(delta_x / d)
            if y < loc[1]:
                a = 2 * math.pi - a
            a -= angle
            start_angle = a
            if a < 0:
                a += math.pi * 2
            start_d = math.floor(a / (0.5 * math.pi))
            a += 2 * angle
            end_angle = a % (math.pi * 2)
            end_d = math.floor(a / (0.5 * math.pi))

            angles[loc][p] = {'angle': angle * 2, 'start_angle': start_angle, 'end_angle': end_angle}
            if len(possible_directions) == 4:
                continue
            for i in range(start_d, end_d + 1):
                if i >= 4:
                    i -= 4
                d = ''
                if i == 0:
                    d = 'E'
                elif i == 1:
                    d = 'N'
                elif i == 2:
                    d = 'W'
                elif i == 3:
                    d = 'S'
                assert d != ''
                possible_directions.add(d)
        domain = list(universal_domain)
        for d in {'E', 'N', 'W', 'S'}:
            if d not in possible_directions:
                for ud in universal_domain:
                    if d in ud and ud in domain:
                        domain.remove(ud)
        radars_domain[loc] = domain
    functions = dict()
    total_factor_size = 0
    for p in phenomena:
        (x, y), ty, radius, ra = phenomena[p]
        ra.sort()
        domains = [[i for i in range(len(radars_domain[z]))] for z in ra]
        sizes = {radars[z]: len(radars_domain[z]) for z in ra}
        f = Tensor(sizes)
        total_factor_size = max(total_factor_size, len(sizes) * len(f))
        names = [radars[z] for z in ra]
        for t in itertools.product(*domains):
            utility = []
            for idx in range(len(ra)):
                loc = ra[idx]
                assignment = radars_domain[loc][t[idx]]
                actions = parse_action(assignment)
                total_covered_angle = 0
                covered_angle = 0
                angle = angles[loc][p]['angle']
                start_angle = angles[loc][p]['start_angle']
                end_angle = angles[loc][p]['end_angle']
                line_segment = []
                if start_angle <= end_angle:
                    line_segment.append([start_angle, end_angle])
                else:
                    line_segment.append([start_angle, math.pi * 2])
                    line_segment.append([0, end_angle])
                added_segs = []
                deleted_segs = []
                for (start, end) in actions:
                    total_covered_angle += (end - start)
                    added_segs.clear()
                    deleted_segs.clear()
                    if len(line_segment) == 0:
                        continue
                    for seg in line_segment:
                        if math.fabs(seg[0] - seg[1]) < 0.0000001:
                            deleted_segs.append(seg)
                            continue
                        if seg[0] <= end + 0.00001 and seg[1] >= start - 0.000001:
                            s = max(seg[0], start)
                            e = min(end, seg[-1])
                            covered_angle += (e - s)
                            if seg[0] >= start - 0.000001 and seg[1] <= end + 0.000001:
                                deleted_segs.append(seg)
                            elif seg[0] <= start and seg[1] <= end:
                                seg[1] = start
                            elif seg[0] <= start and seg[1] >= end:
                                added_segs.append([seg[0], start])
                                added_segs.append([end, seg[1]])
                                deleted_segs.append(seg)
                            elif seg[0] >= start and seg[1] >= end:
                                seg[0] = end
                    for d_seg in deleted_segs:
                        line_segment.remove(d_seg)
                    if len(added_segs) != 0:
                        line_segment += added_segs
                coverage = covered_angle / angle
                if coverage > 0.9999:
                    check = len(line_segment)
                    if check != 0:
                        return False
                coverage_utility = f_c(coverage)
                d = distance(x, y, *loc)
                distance_utility = f_d(d)
                w = total_covered_angle / (math.pi * 2)
                evaluation_utility = f_w(w)
                utility.append(coverage_utility * (beta * distance_utility + (1 - beta) * evaluation_utility))

            if ty == 1:
                u = max(utility)
            else:
                u = f_pp(sum(utility))
            assignment = {names[i]: t[i] for i in range(len(t))}
            f.set_value(assignment, u)
        functions[p] = f
    root = et.Element('instance')
    et.SubElement(root, 'presentation', {'type': 'NDCOP', 'continuous': 'true'})
    agents = et.SubElement(root, 'agents', {'nbAgents': str(len(radars))})
    domains = set()
    for loc in radars:
        rd = radars[loc]
        et.SubElement(agents, 'agent', {'name': rd, 'id': rd[1:], 'description': str(loc)})
        domains.add(len(radars_domain[loc]))
    domains_label = et.SubElement(root, 'domains', {'nbDomains': str(len(domains))})
    domains_info = {}
    idx = 1
    for d in domains:
        name = 'D' + str(idx)
        idx += 1
        e = et.SubElement(domains_label, 'domain', {'name': name, 'nbValues': str(d)})
        e.text = '1..' + str(d)
        domains_info[d] = name
    variables = et.SubElement(root, 'variables', {'nbVariables': str(len(radars))})
    for loc in radars:
        rd = radars[loc]
        domain = len(radars_domain[loc])
        et.SubElement(variables, 'variable', {'agent': rd, 'name': 'X' + rd[1:] + '.1', 'domain': domains_info[domain]})
    constraints = et.SubElement(root, 'constraints', {'nbConstraints': str(len(phenomena))})
    relations = et.SubElement(root, 'relations', {'nbRelations': str(len(phenomena))})
    for p in phenomena:
        scope = [radars[x] for x in phenomena[p][-1]]
        scope = ['X' + x[1:] + '.1' for x in scope]
        scope = ' '.join(scope)
        et.SubElement(constraints, 'constraint', {'name': p, 'arity': str(len(phenomena[p][-1])), 'scope': scope, 'reference': p})
        et.SubElement(relations, 'relation', {'name': p, 'arity': str(len(phenomena[p][-1]))})
    relation_folder = os.path.join(directory, 'relations')
    if not os.path.exists(relation_folder):
        os.makedirs(relation_folder)
    relation_folder = os.path.join(relation_folder, file_name[: -4])
    os.mkdir(relation_folder)
    for p in phenomena:
        f = functions[p]
        domains = [[i for i in range(len(radars_domain[z]))] for z in phenomena[p][-1]]
        names = [radars[z] for z in phenomena[p][-1]]
        file = open(os.path.join(relation_folder, p), 'w')
        cnt = 0
        idx = 0
        for t in itertools.product(*domains):
            if cnt == 1000:
                cnt = 0
                file.write('\n')
            assignment = {names[i]: t[i] for i in range(len(t))}
            u = f.get_value(assignment)
            assert u >= 0
            cnt += 1
            idx += 1
            file.write(str(u))
            if cnt != 1000 and idx != len(f):
                file.write('|')
        file.close()
    xmlstr = minidom.parseString(et.tostring(root)).toprettyxml(indent="   ")
    with open(os.path.join(directory, file_name), "w") as f:
        f.write(xmlstr)
    return True


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def parse_action(action):
    results = []
    half_pi = math.pi / 2
    for d in action:
        if d == 'E':
            results.append((0, half_pi))
        elif d == 'N':
            results.append((half_pi, 2 * half_pi))
        elif d == 'W':
            results.append((2 * half_pi, 3 * half_pi))
        elif d == 'S':
            results.append((3* half_pi, 4 * half_pi))
    return results

def f_pp(value):
    if value <= 1:
        return value / 2.5
    if value <= 2:
        return 0.4 + (value - 1) / 3.333
    if value <= 3:
        return 0.7 + (value - 2) / 5
    return min(1, 0.9 + (value - 3) / 10)


def f_c(value):
    return 0 if value < .95 else 1

def f_d(value):
    if value < 1:
        return 1 - value
    return 0


def f_w(value):
    if value <= 0.25:
        return 1
    if value <= 0.5:
        return 0.5
    return 0.3
