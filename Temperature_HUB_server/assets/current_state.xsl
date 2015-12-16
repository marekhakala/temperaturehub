<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head>
        <title>Temperature HUB - Current state</title>
        <link href="assets?filename=bootstrap.min.css" rel="stylesheet" />
      </head>
      <body>
        <div class="container">
          <div class="row text-center">
            <h1>Temperature HUB - Current state</h1>
          </div>
          <div class="row text-center">
            <p><b>Last update: </b> <xsl:value-of select="response/@timestamp"/> UTC | <a href="/" class="btn btn-xs btn-default">Update</a></p>
            <p><a href="/" class="btn btn-xs btn-primary">Current state</a> | <a href="/history" class="btn btn-xs btn-primary">History</a></p>
            <xsl:for-each select="response/thermometers/thermometer">
              <h3>
                #<xsl:value-of select="@index"/> | <xsl:value-of select="@title"/>
                <span class="label label-default">Lat: <xsl:value-of select="location/latitude"/>, Long: <xsl:value-of select="location/longitude"/>
                </span>
              </h3>
              <i><xsl:value-of select="description"/></i>
              <hr />

              <xsl:for-each select="sensors/sensor">
                <h4>Sensor #<xsl:value-of select="@index"/>
                  <small> (<xsl:value-of select="description"/>)</small>
                </h4>
                <table class="table table-striped table-bordered">
                  <tr>
                    <th>Celsius</th>
                    <th>Fahrenheit</th>
                    <th>Humidity</th>
                  </tr>
                  <tr>
                    <td><xsl:value-of select="values/value[1]"/> &#176;C</td>
                    <td><xsl:value-of select="values/value[2]"/> &#176;F</td>
                    <td><xsl:value-of select="values/value[3]"/> %</td>
                  </tr>
                </table>
              </xsl:for-each>
              <hr />
            </xsl:for-each>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
