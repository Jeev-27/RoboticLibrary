#!/bin/bash

echo "Fixing PAL navigation config files..."

BASE="/tiago_public_ws/src/pal_navigation_cfg_public/pal_navigation_cfg_tiago/config/base/common"

cp "$BASE/global_costmap_plugins_public_sim.yaml" "$BASE/global_costmap_plugins.yaml"
cp "$BASE/local_costmap_plugins_public_sim.yaml" "$BASE/local_costmap_plugins.yaml"

echo "Done. Use local_planner:=eband, not dwa."

