file(REMOVE_RECURSE
  "libgraph-builder.a"
  "libgraph-builder.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang )
  include(CMakeFiles/graph-builder.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
