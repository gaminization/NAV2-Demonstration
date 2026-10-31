# Latched (transient_local) status of the mission server.
uint8 STATE_IDLE=0
uint8 STATE_RUNNING=1
uint8 STATE_SUCCEEDED=2
uint8 STATE_FAILED=3
uint8 STATE_CANCELED=4

builtin_interfaces/Time stamp
string world
string mission_name
uint8 state
uint32 current_waypoint
uint32 total_waypoints
