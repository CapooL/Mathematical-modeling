import networkx as nx
from networkx import bipartite
import numpy
from scipy import sparse

def plotGraph(graph):
    import matplotlib.pyplot as plt
    fig=plt.figure()
    ax=fig.add_subplot(111)
    pos=[(ii[1],ii[0]) for ii in graph.nodes()]
    pos_dict=dict(zip(graph.nodes(),pos))
    nx.draw(graph,pos=pos_dict,ax=ax,with_labels=True)
    plt.show(block=False)
    plt.pause(0)
    return

def formDirected(g,match):

    d=nx.DiGraph()

    for ee in g.edges():
        if ee in match or (ee[1],ee[0]) in match:
            if g.nodes[ee[0]]['bipartite']==0:
                d.add_edge(ee[0],ee[1])
            else:
                d.add_edge(ee[1],ee[0])
        else:
            if g.nodes[ee[0]]['bipartite']==0:
                d.add_edge(ee[1],ee[0])
            else:
                d.add_edge(ee[0],ee[1])

    return d

def enumMaximumMatching(g):
    all_matches=[]

    top = [n for n in g.nodes if g.nodes[n]['bipartite']==0]
    match=bipartite.hopcroft_karp_matching(g, top_nodes=top)

    match2=[]
    for kk,vv in match.items():
        if g.nodes[kk]['bipartite']==0:
            match2.append((kk,vv))
    match=match2
    all_matches.append(match)
    all_matches=enumMaximumMatchingIter(g,match,all_matches,None)
    return all_matches




def enumMaximumMatchingIter(g,match,all_matches,add_e=None):
    d=formDirected(g,match)
    cycles=list(nx.simple_cycles(d))
    if len(cycles)==0:
        all_uncovered=set(g.nodes).difference(set([ii[0] for ii in match]))
        all_uncovered=all_uncovered.difference(set([ii[1] for ii in match]))
        all_uncovered=list(all_uncovered)

        if len(all_uncovered)==0:
            return all_matches
        idx=0
        uncovered=all_uncovered[idx]
        while True:
            if uncovered not in nx.isolates(g):
                paths=nx.single_source_shortest_path(d,uncovered,cutoff=2)
                len2paths=[vv for kk,vv in paths.items() if len(vv)==3]

                if len(len2paths)>0:
                    reversed=False
                    break

                paths_rev=nx.single_source_shortest_path(d.reverse(),uncovered,cutoff=2)
                len2paths=[vv for kk,vv in paths_rev.items() if len(vv)==3]

                if len(len2paths)>0:
                    reversed=True
                    break

            idx+=1
            if idx>len(all_uncovered)-1:
                return all_matches

            uncovered=all_uncovered[idx]
        len2path=len2paths[0]
        if reversed:
            len2path=len2path[::-1]
        len2path=list(zip(len2path[:-1],len2path[1:]))
        new_match=[]
        for ee in d.edges():
            if ee in len2path:
                if g.nodes[ee[1]]['bipartite']==0:
                    new_match.append((ee[1],ee[0]))
            else:
                if g.nodes[ee[0]]['bipartite']==0:
                    new_match.append(ee)
        if add_e is not None:
            for ii in add_e:
                new_match.append(ii)
        all_matches.append(new_match)
        e=set(len2path).difference(set(match))
        e=list(e)[0]
        g_plus=g.copy()
        g_minus=g.copy()
        g_plus.remove_node(e[0])
        g_plus.remove_node(e[1])
        g_minus.remove_edge(e[0],e[1])
        add_e_new=[e,]
        if add_e is not None:
            add_e_new.extend(add_e)
        all_matches=enumMaximumMatchingIter(g_minus,match,all_matches,add_e)
        all_matches=enumMaximumMatchingIter(g_plus,new_match,all_matches,add_e_new)
    else:
        cycle=cycles[0]
        cycle.append(cycle[0])
        cycle=list(zip(cycle[:-1],cycle[1:]))
        new_match=[]
        for ee in d.edges():
            if ee in cycle:
                if g.nodes[ee[1]]['bipartite']==0:
                    new_match.append((ee[1],ee[0]))
            else:
                if g.nodes[ee[0]]['bipartite']==0:
                    new_match.append(ee)
        if add_e is not None:
            for ii in add_e:
                new_match.append(ii)
        all_matches.append(new_match)
        e=set(match).intersection(set(cycle))
        e=list(e)[0]
        g_plus=g.copy()
        g_minus=g.copy()
        g_plus.remove_node(e[0])
        g_plus.remove_node(e[1])
        g_minus.remove_edge(e[0],e[1])
        add_e_new=[e,]
        if add_e is not None:
            add_e_new.extend(add_e)
        all_matches=enumMaximumMatchingIter(g_minus,new_match,all_matches,add_e)
        all_matches=enumMaximumMatchingIter(g_plus,match,all_matches,add_e_new)

    return all_matches

def enumMaximumMatching2(g):
    s1=set(n for n,d in g.nodes(data=True) if d['bipartite']==0)
    s2=set(g)-s1
    n1=len(s1)
    nodes=list(s1)+list(s2)

    adj=nx.adjacency_matrix(g,nodes).tolil()
    all_matches=[]

    match=bipartite.hopcroft_karp_matching(g)

    matchadj=numpy.zeros(adj.shape).astype('int')
    for kk,vv in match.items():
        matchadj[nodes.index(kk),nodes.index(vv)]=1
    matchadj=sparse.lil_matrix(matchadj)

    all_matches.append(matchadj)

    all_matches=enumMaximumMatchingIter2(adj,matchadj,all_matches,n1,None,True)

    all_matches2=[]
    for ii in all_matches:
        match_list=sparse.find(ii[:n1]==1)
        m1=[nodes[jj] for jj in match_list[0]]
        m2=[nodes[jj] for jj in match_list[1]]
        match_list=list(zip(m1,m2))

        all_matches2.append(match_list)
    print('got all')
    return all_matches2


def enumMaximumMatchingIter2(adj,matchadj,all_matches,n1,add_e=None,check_cycle=True):
    if check_cycle:
        d=matchadj.multiply(adj)
        d[n1:,:]=adj[n1:,:]-matchadj[n1:,:].multiply(adj[n1:,:])

        dg=nx.from_numpy_matrix(d.toarray(),create_using=nx.DiGraph())
        cycles=list(nx.simple_cycles(dg))
        if len(cycles)==0:
            check_cycle=False
        else:
            check_cycle=True
    if check_cycle:
        cycle=cycles[0]
        cycle.append(cycle[0])
        cycle=list(zip(cycle[:-1],cycle[1:]))
        new_match=matchadj.copy()
        for ee in cycle:
            if matchadj[ee[0],ee[1]]==1:
                new_match[ee[0],ee[1]]=0
                new_match[ee[1],ee[0]]=0
                e=ee
            else:
                new_match[ee[0],ee[1]]=1
                new_match[ee[1],ee[0]]=1
        if add_e is not None:
            for ii in add_e:
                new_match[ii[0],ii[1]]=1
        all_matches.append(new_match)
        g_plus=adj.copy()
        g_minus=adj.copy()
        g_plus[e[0],:]=0
        g_plus[:,e[1]]=0
        g_plus[:,e[0]]=0
        g_plus[e[1],:]=0
        g_minus[e[0],e[1]]=0
        g_minus[e[1],e[0]]=0
        add_e_new=[e,]
        if add_e is not None:
            add_e_new.extend(add_e)
        all_matches=enumMaximumMatchingIter2(g_minus,new_match,all_matches,n1,add_e,check_cycle)
        all_matches=enumMaximumMatchingIter2(g_plus,matchadj,all_matches,n1,add_e_new,check_cycle)
    else:
        uncovered=numpy.where(numpy.sum(matchadj,axis=1)==0)[0]
        if len(uncovered)==0:
            return all_matches
        paths=[]
        for ii in uncovered:
            aa=adj[ii,:].dot(matchadj)
            if aa.sum()==0:
                continue
            paths.append((ii,int(sparse.find(aa==1)[1][0])))
            if len(paths)>0:
                break
        if len(paths)==0:
            return all_matches
        feas1,feas2=paths[0]
        e=(feas1,int(sparse.find(matchadj[:,feas2]==1)[0]))
        new_match=matchadj.copy()
        new_match[feas2,:]=0
        new_match[:,feas2]=0
        new_match[feas1,e[1]]=1
        new_match[e[1],feas1]=1
        if add_e is not None:
            for ii in add_e:
                new_match[ii[0],ii[1]]=1
        all_matches.append(new_match)
        g_plus=adj.copy()
        g_minus=adj.copy()
        g_plus[e[0],:]=0
        g_plus[:,e[1]]=0
        g_plus[:,e[0]]=0
        g_plus[e[1],:]=0
        g_minus[e[0],e[1]]=0
        g_minus[e[1],e[0]]=0
        add_e_new=[e,]
        if add_e is not None:
            add_e_new.extend(add_e)
        all_matches=enumMaximumMatchingIter2(g_minus,matchadj,all_matches,n1,add_e,check_cycle)
        all_matches=enumMaximumMatchingIter2(g_plus,new_match,all_matches,n1,add_e_new,check_cycle)

    if len(all_matches)%1000==0:
        print('len',len(all_matches))

    return all_matches
def findCycle(adj,n1):
    path=[]
    visited=set()

    def visit(v):
        if v in visited:
            return False
        visited.add(v)
        path.append(v)
        neighbours=sparse.find(adj[v,:]==1)[1]
        for nn in neighbours:
            if nn in path or visit(nn):
                return True
        path.remove(v)
        return False
    nodes=range(n1)
    result=any(visit(v) for v in nodes)
    return result,path
def example1():
    g=nx.Graph()
    edges=[
            [(1,0), (0,0)],[(1,0), (0,1)],[(1,2), (0,0)],[(1,2), (0,1)],[(1,4), (0,2)],[(1,4), (0,3)],
            [(1,4), (0,4)],[(1,5), (0,4)],[(1,6), (0,2)],[(1,6), (0,3)],[(1,7), (0,1)],[(1,7), (0,2)]]

    for ii in edges:
        g.add_node(ii[0],bipartite=0)
        g.add_node(ii[1],bipartite=1)

    g.add_edges_from(edges)
    plotGraph(g)

    all_matches=enumMaximumMatching(g)

    for mm in all_matches:
        g_match=nx.Graph()
        for ii in mm:
            g_match.add_edge(ii[0],ii[1])
        plotGraph(g_match)

if __name__=='__main__':

    example1()