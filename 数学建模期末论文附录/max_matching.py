import networkx as nx


def max_matching():
    # 创建一个空的二分图
    B = nx.Graph()

    # 添加队员和位置节点
    B.add_nodes_from(['A', 'C', 'E', 'F', 'G', 'H'], bipartite=0)  # 队员节点集
    B.add_nodes_from([1, 2, 3, 4, 5], bipartite=1)  # 位置节点集

    # 添加边
    B.add_edges_from([('A', 1), ('A', 2), ('C', 1), ('C', 2),
                      ('E', 3), ('E', 4), ('E', 5), ('F', 5), ('G', 3), ('G', 4),
                      ('H', 2), ('H', 3)])

    # 使用匈牙利算法找到最大匹配
    matching = nx.bipartite.maximum_matching(B)
    file = open('record_1.txt', mode='a', encoding='utf-8')
    print(matching,file=file)
    file.close()
    print(matching)

max_matching()


