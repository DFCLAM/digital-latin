<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	xmlns:xs="http://www.w3.org/2001/XMLSchema"
	xpath-default-namespace="http://www.tei-c.org/ns/1.0"
	xmlns:tei="http://www.tei-c.org/ns/1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="3.0">
	
	<xsl:output encoding="utf-8" method="text" />
	
	<!--
	If true, shows the original document's lectio
	instead of the editor's amendment,
	e.g. choice/sic instead of choice/corr.
	-->
	<xsl:param name="diplomatic" as="xs:boolean">false</xsl:param>
	
	<!--
	If true, put all the text in single line.
	-->
	<xsl:param name="single-line" as="xs:boolean">false</xsl:param>
	
	<xsl:template match="/">
		<xsl:variable name="text">
			<xsl:apply-templates select="./*" />
		</xsl:variable>
		<!-- Normalizing spaces, optionally maintaining the original line breaks -->
		<xsl:for-each select="tokenize($text, '&#xA;')">
			<xsl:value-of select="normalize-space()"/>
			<xsl:if test="position() lt last()">
				<xsl:choose>
					<xsl:when test="$single-line">
						<xsl:text> </xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text>&#xA;</xsl:text>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:if>
		</xsl:for-each>
	</xsl:template>

	<xsl:template match="teiHeader" />

	<xsl:template match="figDesc" />

	<xsl:template match="gap/desc" />
	
	<xsl:template match="text|body|front|back|p|div|div1|div2|div3|div4|div5|div6|div7|head|closer">
		<xsl:apply-templates/>
		<xsl:text>&#xA;</xsl:text>
	</xsl:template>

	<xsl:template match="choice">
		<xsl:choose>
			<xsl:when test="$diplomatic">
				<xsl:apply-templates select="abbr|sic|orig"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:apply-templates select="expan|corr|reg"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template match="text()">
		<xsl:variable name="token">
			<xsl:choose>
				<xsl:when test="normalize-space()=''">
					<xsl:text> </xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="."/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<xsl:value-of select="$token"/>
<!-- 		<xsl:analyze-string select="$token" regex="^\s+(\S+)" flags="m"> -->
<!-- 			<xsl:matching-substring> -->
<!-- 				<xsl:value-of select="regex-group(1)"/> -->
<!-- 			</xsl:matching-substring> -->
<!-- 			<xsl:non-matching-substring> -->
<!-- 				<xsl:value-of select="$token"/> -->
<!-- 			</xsl:non-matching-substring> -->
<!-- 			<xsl:fallback> -->
<!-- 				<xsl:value-of select="$token"/> -->
<!-- 			</xsl:fallback> -->
<!-- 		</xsl:analyze-string> -->

<!-- 		<xsl:variable name="token"> -->
<!-- 			<xsl:analyze-string select="." regex="^\s+(.*)\s*$" flags="m"> -->
<!-- 				<xsl:matching-substring> -->
<!-- 					<xsl:text>&#xA;</xsl:text> -->
<!-- 					<xsl:value-of select="regex-group(1)"/> -->
<!-- 				</xsl:matching-substring> -->
<!-- 				<xsl:non-matching-substring> -->
<!-- 					<xsl:value-of select="."/> -->
<!-- 				</xsl:non-matching-substring> -->
<!-- 				<xsl:fallback> -->
<!-- 					<xsl:value-of select="."/> -->
<!-- 				</xsl:fallback> -->
<!-- 			</xsl:analyze-string> -->
<!-- 		</xsl:variable> -->
<!-- 		<xsl:choose> -->
<!-- 			<xsl:when test="normalize-space($token)=''"> -->
<!-- 				<xsl:text></xsl:text> -->
<!-- 			</xsl:when> -->
<!-- 			<xsl:otherwise> -->
<!-- 				<xsl:value-of select="$token"/> -->
<!-- 			</xsl:otherwise> -->
<!-- 		</xsl:choose> -->
	</xsl:template>
	
</xsl:stylesheet>
