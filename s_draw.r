args = commandArgs(trailingOnly=TRUE)

# Set user R library
.libPaths( c( Sys.getenv("R_LIBS_USER"), .libPaths() ) )

# Check if sp is installed
if(!("sp" %in% rownames(installed.packages()))){
  install.packages("sp", repos="http://cran.us.r-project.org")
}
require(sp)

# Check if rstudioapi is installed
if(!("rstudioapi" %in% rownames(installed.packages()))){
  install.packages("rstudioapi", repos="http://cran.us.r-project.org")
}
require(rstudioapi)

# Check if rgdal is installed
if(!("rgdal" %in% rownames(installed.packages()))){
  install.packages("rgdal", repos="http://cran.us.r-project.org")
}
require(rgdal)

# Check if sf is installed
if(!("sf" %in% rownames(installed.packages()))){
  install.packages("sf", repos="http://cran.us.r-project.org")
}
require(sf)

# Check if SDraw is installed
if(!("SDraw" %in% rownames(installed.packages()))){
  install.packages("SDraw", repos="http://cran.us.r-project.org")
}
require(SDraw)

sdrawPlugin <- function(n, type, source) {
  tryCatch(
      {
        # read in the shapfile to work on
        shpFile <- st_read(as.character(source))

        # convert shapefile to spatial data frame
        shpFile_df <- as(shpFile, "Spatial")

        # operate on the shpfile read in
        newShapeFile <- sdraw(shpFile_df, as.numeric(n), toString(type))

        # Create timestamp
        timestamp = gsub('[-:]', '', Sys.time())
        timestamp = gsub('^| ', '_', timestamp)

        layer <- paste(toString(type),sub("\\.shp$", "", basename(toString(as.character(source)))), timestamp, sep="_")
        dsn <-dirname(toString(as.character(source)))

        # Generate new shapefiles
        if (!is.null(newShapeFile)) {
          writeOGR(obj=newShapeFile,dsn=dsn,
            layer = layer, 
            driver = 'ESRI Shapefile')
        }
        return(layer)
      },
      error = function(c) {
        return(c)
      })
}
sdrawPlugin(args[1], args[2], args[3])