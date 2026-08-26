# diagram-editor Specification

## Purpose
TBD - created by archiving change add-diagram-editor. Update Purpose after archive.

## Requirements

### Requirement: The canvas is interactive

The editor SHALL render the diagram in an interactive React Flow canvas where nodes can be moved, selected, connected, and deleted. Pan, zoom, and the minimap remain available.

#### Scenario: Nodes are draggable

- **WHEN** the user drags a node on the canvas
- **THEN** the node moves to the new position
- **AND** the node's new position is reflected in the serialized diagram

#### Scenario: A node is selectable

- **WHEN** the user clicks a node
- **THEN** the node becomes selected (visually distinct)

### Requirement: Create nodes by dragging from the palette

The editor SHALL let the user drag a component from the palette and drop it on the canvas to create a new node of that type at the drop position.

#### Scenario: Drop creates a typed node

- **WHEN** the user drags the "Database" palette card and drops it on the canvas
- **THEN** a new node of type `database` is added at the drop location
- **AND** the node has a non-empty default label and a unique id

#### Scenario: Dropped node persists in the serialized diagram

- **WHEN** a node is created by drop and the graph is serialized
- **THEN** the resulting `Diagram` includes that node with its type and position

### Requirement: Connect nodes by their handles

The editor SHALL let the user create an edge by dragging from one node's handle to another node's handle.

#### Scenario: Handle-to-handle creates an edge

- **WHEN** the user drags from node A's source handle to node B's target handle
- **THEN** an edge from A to B is added with a unique id
- **AND** the serialized diagram contains that edge

#### Scenario: Self-loops are rejected

- **WHEN** the user attempts to connect a node to itself
- **THEN** no edge is created

### Requirement: Rename a node

The editor SHALL let the user edit a node's label.

#### Scenario: Inline rename updates the label

- **WHEN** the user double-clicks a node and types a new label
- **THEN** the node displays the new label
- **AND** the serialized diagram reflects the new label

### Requirement: Delete nodes and edges

The editor SHALL let the user delete selected nodes and edges. Deleting a node SHALL also remove edges incident to it.

#### Scenario: Deleting a node prunes its edges

- **WHEN** the user deletes a node that has connected edges
- **THEN** the node is removed
- **AND** every edge whose source or target was that node is also removed

#### Scenario: Deleting an edge leaves nodes intact

- **WHEN** the user deletes an edge
- **THEN** the edge is removed and both endpoint nodes remain

### Requirement: Graph round-trips to the Diagram schema

The editor SHALL serialize the live canvas to a valid Tangram `Diagram` and SHALL reconstruct the canvas from a `Diagram` without losing node ids, types, labels, positions, or edges.

#### Scenario: Round-trip preserves the graph

- **WHEN** a diagram is loaded, converted to the canvas, then serialized back with no edits
- **THEN** the serialized diagram has the same node ids, types, positions, and the same edges as the original

#### Scenario: Serialized diagram is schema-valid

- **WHEN** the canvas is serialized
- **THEN** every edge references node ids that exist in the diagram
- **AND** node ids are unique

### Requirement: Edits persist automatically

The editor SHALL persist edits to storage automatically and SHALL surface the save state to the user. Persistence uses the existing diagram storage route (upsert by id).

#### Scenario: An edit triggers a debounced save

- **WHEN** the user makes an edit and then pauses
- **THEN** the editor serializes the graph and upserts it via the storage route
- **AND** the topbar shows a saved indicator on success

#### Scenario: A blank canvas gains an id before its first save

- **WHEN** the user adds the first node to a blank (unsaved) canvas
- **THEN** the diagram is assigned a client-generated id and default metadata
- **AND** the subsequent save upserts under that id

#### Scenario: A failed save is surfaced

- **WHEN** a save request fails
- **THEN** the topbar shows a save-failed state rather than silently dropping the edit

#### Scenario: The Save button flushes immediately

- **WHEN** the user has unsaved edits and clicks the Save button
- **THEN** the pending debounced save is cancelled and the graph is saved right away
- **AND** the Save button is disabled while there are no unsaved changes
