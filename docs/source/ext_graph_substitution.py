"""
Custom Sphinx extension to allow substitution in Graphviz Graph blocks.

Adapted from source: https://stackoverflow.com/questions/44761197/how-to-use-substitution-definitions-with-code-blocks
"""

from typing import List

from sphinx.application import Sphinx
from sphinx.ext.graphviz import GraphvizSimple


class SubstitutionGraph(GraphvizSimple):  # type: ignore
    """
    Similar to CodeBlock but replaces placeholders with variables.
    """

    def run(self) -> List:
        """
        Replace placeholders with given variables.
        """
        if 'digraph' in self.name:
            self.name = 'digraph'
        else:
            self.name = 'graph'
        app = self.state.document.settings.env.app
        new_content = []
        self.content = self.content  # type: List[str]
        existing_content = self.content
        if self.name == 'digraph':
            substitutions = app.config.digraph_substitutions
        else:
            substitutions = app.config.graph_substitutions
        for item in existing_content:
            is_comment = False
            for pair in substitutions:
                original, replacement = pair
                is_comment = item.find('|#|') >= 0
                if not is_comment:
                    item = item.replace(original, replacement)
            if not is_comment:
                new_content.append(item)

        self.content = new_content
        return list(GraphvizSimple.run(self))


def setup(app: Sphinx) -> None:
    """
    Add the custom directives to Sphinx.
    """
    app.add_config_value('graph_substitutions', [], 'html')
    app.add_config_value('digraph_substitutions', [], 'html')
    app.add_directive('substitution-graph', SubstitutionGraph)
    app.add_directive('substitution-digraph', SubstitutionGraph)
