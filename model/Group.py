class Group:
    def __init__(self, model, name):
        self._model = model
        self._name = name

    @property
    def _faces(self):
        """Return all faces belonging to the group"""
        return [face for face in self._model._faces if face._group == self]

    @property
    def _bbox(self):
        """Get bounding box for group"""
        bbox = [np.array([0., 0., 0.]), np.array([0., 0., 0.])]
        for face in self._faces:
            for idx in face._vertex_ids:
                vertex = self._model._vertices[idx]
                bbox[0][0] = min(bbox[0][0], vertex[0])
                bbox[0][1] = min(bbox[0][1], vertex[1])
                bbox[0][2] = min(bbox[0][2], vertex[2])
                bbox[1][0] = max(bbox[1][0], vertex[0])
                bbox[1][1] = max(bbox[1][1], vertex[1])
                bbox[1][2] = max(bbox[1][2], vertex[2])
        return bbox

    def get_faces_by_tag(self, tag):
        return [face for face in self._faces if tag in face._tags]