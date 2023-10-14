#ifndef TRANSFORMED_VIEW_HPP
#define TRANSFORMED_VIEW_HPP

class TransformedView
{
public:
	TransformedView() = default;
	TransformedView(int width, int height);

	void SetDimensions(int width, int height);

private:
	float m_OffsetX = 0.0f;
	float m_OffsetY = 0.0f;

	float m_PanStartX = 0.0f;
	float m_PanStartY = 0.0f;

	float m_ScaleX = 1.0f;
	float m_ScaleY = 1.0f;

	int m_ScreenWidth;
	int m_ScreenHeight;

public:
	void WorldToScreen(float worldX, float worldY, int& screenX, int& screenY);
	void ScreenToWorld(int screenX, int screenY, float& worldX, float& worldY);

	void StartPan(float x, float y);
	void ProgressPan(float x, float y);

	void Zoom(float x, float y, float factor);

	void Translate(float x, float y);
	void Scale(float x, float y);

	float GetScaleX();
	float GetScaleY();

	float GetOffsetX();
	float GetOffsetY();

	void ScreenToWorldBounds(float& x, float& y, float& width, float& height);

};

#ifdef TRANSFORMED_VIEW_IMPL
#undef TRANSFORMED_VIEW_IMPL

TransformedView::TransformedView(int width, int height)
{
	SetDimensions(width, height);
}

void TransformedView::SetDimensions(int width, int height)
{
	m_ScreenWidth = width;
	m_ScreenHeight = height;
}

void TransformedView::WorldToScreen(float worldX, float worldY, int& screenX, int& screenY)
{
	screenX = int((worldX - m_OffsetX) * m_ScaleX);
	screenY = int((worldY - m_OffsetY) * m_ScaleY);
}

void TransformedView::ScreenToWorld(int screenX, int screenY, float& worldX, float& worldY)
{
	worldX = (float)screenX / m_ScaleX + m_OffsetX;
	worldY = (float)screenY / m_ScaleY + m_OffsetY;
}

void TransformedView::StartPan(float x, float y)
{
	m_PanStartX = x;
	m_PanStartY = y;
}

void TransformedView::ProgressPan(float x, float y)
{
	m_OffsetX -= (x - m_PanStartX) / m_ScaleX;
	m_OffsetY -= (y - m_PanStartY) / m_ScaleY;

	m_PanStartX = x;
	m_PanStartY = y;
}

void TransformedView::Zoom(float x, float y, float factor)
{
	float beforeZoomX, beforeZoomY;
	ScreenToWorld(x, y, beforeZoomX, beforeZoomY);

	m_ScaleX *= factor;
	m_ScaleY *= factor;

	float afterZoomX, afterZoomY;
	ScreenToWorld(x, y, afterZoomX, afterZoomY);

	m_OffsetX += beforeZoomX - afterZoomX;
	m_OffsetY += beforeZoomY - afterZoomY;
}

void TransformedView::Translate(float x, float y)
{
	m_OffsetX = x;
	m_OffsetY = y;
}

void TransformedView::Scale(float x, float y)
{
	m_ScaleX = x;
	m_ScaleY = y;
}

float TransformedView::GetOffsetX() { return m_OffsetX; }
float TransformedView::GetOffsetY() { return m_OffsetY; }

float TransformedView::GetScaleX() { return m_ScaleX; }
float TransformedView::GetScaleY() { return m_ScaleY; }

void TransformedView::ScreenToWorldBounds(float& x, float& y, float& width, float& height)
{
	ScreenToWorld(0, 0, x, y);
	ScreenToWorld(m_ScreenWidth, m_ScreenHeight, width, height);
}

#endif

#endif
