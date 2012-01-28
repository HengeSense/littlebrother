<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="text" />

	<xsl:template match="/">
		<xsl:for-each select="html/body/div[@id='content']/div[@id='bodyContent']/div[@class='mw-content-ltr']/ul/li">
			<xsl:value-of select="a[1]/text()"/>,<xsl:value-of select="a[2]/text()"/>
			<xsl:text>
</xsl:text>
		</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>
