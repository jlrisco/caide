package util;
import com.mongodb.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;

import org.bson.Document;
import org.bson.conversions.Bson;

import java.util.LinkedList;
import java.util.logging.Logger;

public class ManagerMongoDB {
	// Constants
	protected static final Logger LOGGER = Logger.getLogger(ManagerMongoDB.class.getName());
	protected static final String host = "localhost";
	protected static final int port = 27017;
	protected static final String database = "mainDatabase";
	
	// Attributes
	protected MongoDatabase mongoDB;
	protected MongoClient mongoClient;
	
	// Constructors
	protected ManagerMongoDB(){
		this.connect(host, port, database);
	}
	
	protected ManagerMongoDB(String database){
		this.connect(host, port, database);
	}
	
	protected ManagerMongoDB(String host, int port, String database){
		this.connect(host, port, database);
	}
	
	// Methods
	protected void connect(String host, int port, String database) {
		try {
			this.mongoClient = new MongoClient(host, port);
			this.mongoDB = mongoClient.getDatabase(database);
		} catch(Exception e) {
			LOGGER.severe(e.getLocalizedMessage());
		}
	}

	public static void dropDatabase(String database) {
		dropDatabase(host, port,database);
	}
	
	@SuppressWarnings("deprecation")
	public static void dropDatabase(String host, int port, String database) {
		try {
			final MongoClient m = new MongoClient(host, port);
		    m.dropDatabase(database);
		} catch(Exception e){
			LOGGER.info(e.getLocalizedMessage());
		}
	}
	
	public void close() {
		try {
			this.mongoClient.close();
		}catch(Exception e) {
			LOGGER.severe(e.getLocalizedMessage());
		}
	}
	
	protected void insertDocument(String collectionName, Document document) {
		try {
			MongoCollection<Document> collection = this.mongoDB.getCollection(collectionName);
			collection.insertOne(document);
		} catch(Exception e) {
			LOGGER.severe(e.getLocalizedMessage());
		}
	}
	
	protected LinkedList<Document> getDocuments(String collectionName, Document condition) {
		LinkedList<Document> rows = new LinkedList<Document>();
		try {
			MongoCollection<Document> collection = this.mongoDB.getCollection(collectionName);
			MongoCursor<Document> resultDocuments = collection.find(condition).iterator();
			while (resultDocuments.hasNext()) {
			    rows.add(resultDocuments.next());
			}
		}catch(Exception e){
			LOGGER.severe(e.getLocalizedMessage());
		}
		return rows;
	}
	
	protected LinkedList<Document> getDocuments(String collectionName, Bson condition) {
		LinkedList<Document> rows = new LinkedList<Document>();
		try {
			MongoCollection<Document> collection = this.mongoDB.getCollection(collectionName);
			MongoCursor<Document> resultDocuments = collection.find(condition).iterator();
			while (resultDocuments.hasNext()) {
			    rows.add(resultDocuments.next());
			}
		}catch(Exception e){
			LOGGER.severe(e.getLocalizedMessage());
		}
		return rows;
	}
}
