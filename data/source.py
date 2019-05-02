import _config as config
import sys
from rdflib import Graph, URIRef
from rdflib.namespace import SKOS
import markdown
import pickle
import os
import re
from pprint import pprint


class Source:
    VOC_TYPES = [
        'http://purl.org/vocommons/voaf#Vocabulary',
        'http://www.w3.org/2004/02/skos/core#ConceptScheme',
        'http://www.w3.org/2004/02/skos/core#ConceptCollection',
        'http://www.w3.org/2004/02/skos/core#Concept',
    ]

    @staticmethod
    def load_pickle_graph(vocab_id):
        try:
            with open(os.path.join(config.APP_DIR, 'vocab_files', vocab_id + '.p'), 'rb') as f:
                g = pickle.load(f)
                f.close()
                return g
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def pickle_to_file(vocab_id, g):
        print('Pickling file: {}'.format(vocab_id))
        path = os.path.join(config.APP_DIR, 'vocab_files', vocab_id)
        # TODO: Check if file_name already has extension
        with open(path + '.p', 'wb') as f:
            pickle.dump(g, f)
            f.close()

        g.serialize(path + '.ttl', format='turtle')

    def _delegator(self, function_name):
        """
        Delegates a call to this upper class to one of its specialised child classes

        :return: a call to a specialised method of a class inheriting from this class
        """
        # specialised sources that this instance knows about
        from data.source_RVA import RVA
        from data.source_FILE import FILE
        from data.source_VOCBENCH import VOCBENCH
        from data.source_SPARQL import SPARQL

        # for this vocab, identified by vocab_id, find its source type
        source_type = config.VOCABS[self.vocab_id].get('source')

        # delegate the constructor of this vocab's source the the specialised source, based on source_type
        if source_type == config.VocabSource.FILE:
            return getattr(FILE(self.vocab_id, self.request), function_name)
        elif source_type == config.VocabSource.RVA:
            return getattr(RVA(self.vocab_id, self.request), function_name)
        elif source_type == config.VocabSource.VOCBENCH:
            return getattr(VOCBENCH(self.vocab_id, self.request), function_name)
        elif source_type == config.VocabSource.SPARQL:
            return getattr(SPARQL(self.vocab_id, self.request), function_name)

    def __init__(self, vocab_id, request):
        self.vocab_id = vocab_id
        self.request = request

    @classmethod
    def list_vocabularies(self):
        pass

    def list_collections(self):
        return self._delegator(sys._getframe().f_code.co_name)()

    def list_concepts(self):
        return self._delegator(sys._getframe().f_code.co_name)()

    def get_vocabulary(self):
        return self._delegator(sys._getframe().f_code.co_name)()

    def get_collection(self, uri):
        return self._delegator(sys._getframe().f_code.co_name)(uri)

    def get_concept(self, uri):
        return self._delegator(sys._getframe().f_code.co_name)(uri)

    def get_concept_hierarchy(self):
        return self._delegator(sys._getframe().f_code.co_name)()

    def get_object_class(self, uri):
        """Gets the class of the object.

        Classes restricted to being one of voaf:Vocabulary, skos:ConceptScheme, skos:Collection or skos:Collection

        :param uri: the URI of the object

        :return: the URI of the class of the object
        :rtype: :class:`string`
        """
        return self._delegator(sys._getframe().f_code.co_name)(uri)

    def get_ttl(self):
        return self._delegator(sys._getframe().f_code.co_name)()

    @staticmethod
    def get_prefLabel_from_uri(uri):
        return ' '.join(str(uri).split('#')[-1].split('/')[-1].split('_'))

    @staticmethod
    def get_narrowers(uri, depth):
        """
        Recursively get all skos:narrower properties as a list.

        :param uri: URI node
        :param depth: The current depth
        :param g: The graph
        :return: list of tuples(tree_depth, uri, prefLabel)
        :rtype: list
        """
        depth += 1

        # Some RVA sources won't load on first try, so ..
        # if failed, try load again.
        g = None
        max_attempts = 10
        for i in range(max_attempts):
            try:
                g = Graph().parse(uri + '.ttl', format='turtle')
                break
            except:
                print('Failed to load resource at URI {}. Attempt: {}.'.format(uri, i+1))
        if not g:
            raise Exception('Failed to load Graph from {}. Maximum attempts exceeded {}.'.format(uri, max_attempts))

        items = []
        for s, p, o in g.triples((None, SKOS.broader, URIRef(uri))):
            items.append((depth, str(s), Source.get_prefLabel_from_uri(s)))
        items.sort(key=lambda x: x[2])
        count = 0
        for item in items:
            count += 1
            new_items = Source.get_narrowers(item[1], item[0])
            items = items[:count] + new_items + items[count:]
            count += len(new_items)
        return items

    @staticmethod
    def draw_concept_hierarchy(hierarchy, request, id):
#===============================================================================
#         tab = '\t'
#         previous_length = 1
# 
#         text = ''
#         tracked_items = []
#         for item in hierarchy:
#             mult = None
# 
#             if item[0] > previous_length + 2: # SPARQL query error on length value
#                 for tracked_item in tracked_items:
#                     if tracked_item['name'] == item[3]:
#                         mult = tracked_item['indent'] + 1
# 
#             if mult is None:
#                 found = False
#                 for tracked_item in tracked_items:
#                     if tracked_item['name'] == item[3]:
#                         found = True
#                 if not found:
#                     mult = 0
# 
#             if mult is None:#else: # everything is normal
#                 mult = item[0] - 1
# 
#             tag = str(mult+1) # indent info to be displayed
# 
#             import helper as h
#             t = tab * mult + '* [' + item[2] + '](' + request.url_root + 'object?vocab_id=' + id + '&uri=' + h.url_encode(item[1]) + ') (' + tag + ')\n'
#             text += t
#             previous_length = mult
#             tracked_items.append({'name': item[1], 'indent': mult})
# 
#         return markdown.markdown(text)
#===============================================================================
        pprint(hierarchy)
        
        current_level = 0
        html = '''
<div class="treeview">'''
        
        for item_index in range(len(hierarchy)):
            item_level, item_uri, item_name, _broader_uri = hierarchy[item_index]
            
            if item_index < len(hierarchy) - 1:
                next_item_level = hierarchy[item_index + 1][0]
            else:
                next_item_level = 1
                
            print('item_level: {} current_level: {} next_item_level: {}'.format(item_level, current_level, next_item_level))
            
            if next_item_level > item_level: # Item has children
                html += '''
{indent}<details>'''.format(indent='  '*(item_level))      
          
            # Write summary
            html += '''
{indent}<summary id="{item_id}"><a href={item_uri}>{item_name}</a></summary>'''.format(
    indent='  '*item_level, 
    item_id=re.search('/([^/]+)(/*)$', item_uri).group(1),
    item_name=('- - - '*(item_level-1))+item_name,
    item_uri=item_uri
    )
            # Close of levels of detail if going from higher to lower level
            for level in range(item_level, next_item_level, -1):
                print('Closing level {}'.format(level))
                html += '''
{indent}</details>'''.format(indent='  '*(level-1))          

        # Close off treeview definition
        html += '''
</div>
'''
        
        #print(html)
        return html      