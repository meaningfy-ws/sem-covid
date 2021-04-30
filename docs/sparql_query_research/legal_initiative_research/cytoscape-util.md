# name shortening 

Apply to the node `name` column  the following formula:

```
=IF(${shared name}<>$namespace, SUBSTITUTE(${shared name},$namespace,""), ${shared name} )
```

Apply to the edge `name` column  the following formula:

```
=IF(${shared interaction}<>$namespace, SUBSTITUTE(${shared interaction},$namespace,""), ${shared interaction} )
```



