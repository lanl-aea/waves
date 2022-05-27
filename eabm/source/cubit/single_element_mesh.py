# cubit 15.4

# Mesh
open "single_element_partition.cub"
surface 1  size {global_seed}
mesh surface 1
set duplicate block elements off

# Nodesets
nodeset 1 add vertex 1
nodeset 1 name "bottom_left"
nodeset 2 add vertex 2
nodeset 2 name "bottom_right"
nodeset 3 add vertex 3
nodeset 3 name "top_right"
nodeset 4 add vertex 4
nodeset 4 name "top_left"

# Blocks
block 1 add surface 1
block 1 name "ELEMENTS" Element type QUAD

# Export
export abaqus "single_element.inp"  partial dimension 2 block 1  overwrite  everything
