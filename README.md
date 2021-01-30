# law-fetcher
A module for gathering documents from various legal sources

Example on how to use the `CellarAdapter` to retrieve treaties document items:
```python
from adapters.cellar_adapter import CellarAdapter
ca = CellarAdapter()

treaties = ca.get_treaties()

items = ca.get_treaty_items(ca._extract_values(treaties, 'work'))
item_links = ca._extract_values(items, 'item')

document_paths = list()
for link in item_links[:10]:
    document_paths.append(ca.retrieve_document('some/path', link))
```
`document_paths` will contain the locations of the saved files.