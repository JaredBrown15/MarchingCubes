#pragma once
// #include <vector>
#include <glm/glm.hpp>

struct SDF_Point
{
    const glm::vec3 coord; // x, y, z coordinate of the point
    const int distance;    // Distance from object surface (negative = inside, positive = outside)
};

struct SDF
{
    const std::vector<SDF_Point> &points;
    size_t size; // size in one dimension (assumed cube)
};

std::vector<glm::vec3> computeMesh(const SDF &sdf);

void renderMesh(const float &mesh);
