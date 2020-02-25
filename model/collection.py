from pyldapi import Renderer, Profile
from flask import Response, render_template
from rdflib import Graph
from flask import g

class Collection:
    def __init__(
            self,
            vocab_id,
            prefLabel,
            definition,
            members,
            source,
    ):
        self.vocab_id = vocab_id
        self.prefLabel = prefLabel
        self.definition = definition
        self.members = members
        self.source = source


class CollectionRenderer(Renderer):
    def __init__(self, request, collection):
        self.profiles = self._add_skos_view()
        self.navs = []  # TODO: add in other nav items for Collection

        self.collection = collection

        super().__init__(
            request,
            request.values.get('uri'),
            self.collection.uri,
            self.profiles,
            'skos'
        )

    def _add_skos_view(self):
        return {
            'skos': Profile(
                label='https://www.w3.org/TR/skos-reference/',
                comment='Simple Knowledge Organization System (SKOS) is a W3C recommendation designed for representation of thesauri, classification schemes, '
                'taxonomies, subject-heading systems, or any other type of structured controlled vocabulary.',
                mediatypes=['text/html', 'application/json'] + self.RDF_MEDIA_TYPES,
                default_mediatype='text/html',
                languages=['en'],  # default 'en' only for now
                profile_uri='http://www.w3.org/2004/02/skos/core#'
            )
        }

    def render(self):
        # try returning alt profile
        response = super().render()
        if response is not None:
            return response
        elif self.profile == 'skos':
            if self.mediatype in Renderer.RDF_MEDIA_TYPES:
                return self._render_skos_rdf()
            else:
                return self._render_skos_html()

    def _render_skos_rdf(self):
        # get Collection RDF
        # TODO: re-assemble RDF from Concept object
        graph = Graph()

        # serialise in the appropriate RDF format
        if self.mediatype in ['application/rdf+json', 'application/json']:
            return graph.serialize(format='json-ld')
        else:
            return graph.serialize(format=self.mediatype)

    def _render_skos_html(self):
        _template_context = {
            'vocab_id': self.request.values.get('vocab_id'),
            'vocab_title': g.VOCABS[self.request.values.get('vocab_id')].title,
            'uri': self.request.values.get('uri'),
            'collection': self.collection,
            'title': 'Collection: ' + self.collection.prefLabel,
            'navs': self.navs
        }

        return Response(
            render_template(
                'collection.html',
                **_template_context
            ),
            headers=self.headers
        )
