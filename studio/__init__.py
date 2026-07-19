"""OpenVideoStudio — open-source conversational video-production studio.

Milestone 0: canonical scene graph + end-to-end CLI pipeline.
"""

__version__ = "0.1.0"

# Bumping RENDERER_VERSION invalidates every rendered_fingerprint, forcing a
# full re-render on the next build. Bump when clip/slide rendering changes in a
# way that should regenerate existing projects' assets.
RENDERER_VERSION = "1"
