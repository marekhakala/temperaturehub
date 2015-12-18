<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head>
        <title>Temperature HUB - History</title>
        <link href="assets?filename=bootstrap.min.css" rel="stylesheet" />
      </head>
      <body>
        <div class="container">
          <div class="row text-center">
            <h1>Temperature HUB - History</h1>
          </div>
          <div class="row text-center">
            <hr />
            <p><b>Last update: </b> <xsl:value-of select="response/@timestamp"/> UTC | <a href="/" class="btn btn-xs btn-primary">Current state</a></p>
            <xsl:for-each select="response/thermometers/thermometer">
                #<xsl:value-of select="@index"/> | <b><xsl:value-of select="@title"/></b> |
                <span class="label label-default">Lat: <xsl:value-of select="location/latitude"/>, Long: <xsl:value-of select="location/longitude"/></span> | <i><xsl:value-of select="description"/></i>
                <hr />
                <xsl:for-each select="sensors/sensor">
                  Sensor #<xsl:value-of select="@index"/> - <small><xsl:value-of select="description"/></small><br />
                </xsl:for-each>
                <hr />
            </xsl:for-each>
            <hr />
            <p><b>Filter: </b> <xsl:value-of select="response/filter/from"/> UTC - <xsl:value-of select="response/filter/to"/> UTC</p>
            <p><b>Thermometers: </b>
              <xsl:for-each select="response/thermometersids/thermometerid">
                <xsl:element name="a">
                  <xsl:attribute name="href">/history?thermometer=<xsl:value-of select="."/></xsl:attribute>
                  <xsl:attribute name="class">
                    btn btn-xs <xsl:if test="./@current='true'">btn-primary</xsl:if>
                    <xsl:if test="not(./@current)">btn-default</xsl:if>
                  </xsl:attribute>
                  <xsl:value-of select="."/>
                </xsl:element>&#160;
              </xsl:for-each>
            </p>
            <hr />
            <p>
              <b>Page: </b> <xsl:value-of select="response/filter/page"/>
            </p>
            <p>
                <xsl:for-each select="response/pages/page">
                  <xsl:element name="a">
                    <xsl:attribute name="href">/history?thermometer=<xsl:value-of select="./@thermometer"/><xsl:text disable-output-escaping="yes">&amp;</xsl:text>page=<xsl:value-of select="./@index"/></xsl:attribute>
                    <xsl:attribute name="class">
                      btn btn-xs <xsl:if test="./@current='true'">btn-primary</xsl:if>
                      <xsl:if test="not(./@current)">btn-default</xsl:if>
                    </xsl:attribute>
                    <xsl:value-of select="."/>
                  </xsl:element>&#160;
                </xsl:for-each>
            </p>
            <hr />
            <table class="table table-striped table-bordered table-hover">
              <tr>
                <th>Sensor id</th>
                <th>Celsius</th>
                <th>Fahrenheit</th>
                <th>Humidity</th>
                <th>Date</th>
              </tr>
              <xsl:for-each select="response/values/sensor">
                <tr>
                  <td><xsl:value-of select="@sensorid"/></td>
                  <td><xsl:value-of select="value[1]"/> &#176;C</td>
                  <td><xsl:value-of select="value[2]"/> &#176;F</td>
                  <td><xsl:value-of select="value[3]"/> %</td>
                  <td><xsl:value-of select="@timestamp"/> UTC</td>
                </tr>
              </xsl:for-each>
            </table>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
